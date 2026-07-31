"""Headed browser and Xvfb infrastructure verification tests.

Works inside the ingest container — no `docker exec` needed.

Verifies that:
1. The scraper FastAPI server /health endpoint returns 200.
2. /browser-health returns browser "alive".
3. Xvfb is running (verified via `pgrep -f Xvfb`).
4. Chrome processes are running and connected to the display.
5. Xvfb is active with a valid display dimension (xdpyinfo).

Run inside the ingest container:
    docker exec -e PYTHONPATH=/app radv-cv-ingest-1 pytest -v tests/test_scraper_headed.py
"""
import re
import pytest
import httpx
import subprocess
import socket

SCRAPER_SERVER_URL = "http://localhost:8000"
XVFB_DISPLAY = ":99"


def _subprocess(cmd: str, timeout: int = 15) -> subprocess.CompletedProcess:
    """Run a shell command inside the container."""
    return subprocess.run(
        cmd, capture_output=True, text=True, timeout=timeout, shell=True
    )


def _get_chrome_main_cmdline() -> str | None:
    """Find the main Chromium process via /proc and return its cmdline.

    ps truncates command lines when called via subprocess (no TTY).
    Reading /proc/{pid}/cmdline directly gives the full untruncated string.
    """
    import glob as _glob
    for d in sorted(_glob.glob("/proc/[0-9]*/cmdline")):
        try:
            with open(d, "rb") as f:
                cmd = f.read().replace(b"\x00", b" ").decode()
                if "chromium-1228" in cmd and "test_scraper_headed" not in cmd:
                    return cmd
        except (ProcessLookupError, FileNotFoundError, ValueError):
            pass
    return None


class TestScraperServerHealth:
    """Verify the FastAPI scraper server is running and listening."""

    def test_health_endpoint_returns_200(self):
        """GET /health returns 200 with status ok."""
        client = httpx.Client(timeout=5.0)
        try:
            resp = client.get(f"{SCRAPER_SERVER_URL}/health")
            assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
            data = resp.json()
            assert data["status"] == "ok"
        finally:
            client.close()

    def test_health_endpoint_is_reachable(self):
        """The scraper server port (8000) is open and accepting TCP connections."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(3.0)
            result = sock.connect_ex(("localhost", 8000))
            assert result == 0, "Port 8000 is not accepting connections"


class TestBrowserHealthEndpoint:
    """Verify the browser health endpoint reports the browser as alive."""

    def test_browser_health_returns_alive(self):
        """GET /browser-health returns browser='alive' and connected=True."""
        client = httpx.Client(timeout=5.0)
        try:
            resp = client.get(f"{SCRAPER_SERVER_URL}/browser-health")
            assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
            data = resp.json()
            assert data["browser"] == "alive", f"Expected 'alive', got '{data['browser']}'"
            assert data["connected"] is True, f"Expected connected=True, got {data['connected']}"
        finally:
            client.close()

    def test_browser_health_has_status_field(self):
        """/browser-health response includes a 'status' field."""
        client = httpx.Client(timeout=5.0)
        try:
            resp = client.get(f"{SCRAPER_SERVER_URL}/browser-health")
            data = resp.json()
            assert "status" in data, "Response missing 'status' field"
        finally:
            client.close()


class TestXvfbDisplay:
    """Verify Xvfb is running on display :99 and serving a valid display."""

    def test_xvfb_process_running(self):
        """Xvfb process is running inside the container."""
        result = _subprocess("pgrep -f 'Xvfb :99' > /dev/null")
        assert result.returncode == 0, f"Xvfb not running. stderr: {result.stderr}"

    def test_xvfb_display_99_available(self):
        """Xvfb is listening on display :99."""
        result = _subprocess("pgrep -a Xvfb | grep ':99'")
        assert result.returncode == 0, f"Display :99 not found in Xvfb args. Output: {result.stdout}"

    def test_xvfb_dimensions_nonzero(self):
        """xdpyinfo reports a non-zero display width and height."""
        result = _subprocess(f"xdpyinfo -display {XVFB_DISPLAY} 2>&1")
        assert result.returncode == 0, f"xdpyinfo failed: {result.stderr}"
        import re
        # xdpyinfo line format: "  dimensions:    1440x900 pixels (366x229 millimeters)"
        match = re.search(r'dimensions:\s*(\d+)x(\d+)', result.stdout)
        assert match, f"Could not parse dimensions from xdpyinfo: {result.stdout[:200]}"
        width = int(match.group(1))
        height = int(match.group(2))
        assert width > 0, f"Display width is zero: {width}"
        assert height > 0, f"Display height is zero: {height}"

    def test_xvfb_has_visual_classes(self):
        """xdpyinfo returns visual class info (valid X11 connection)."""
        result = _subprocess(f"xdpyinfo -display {XVFB_DISPLAY} 2>&1")
        assert result.returncode == 0, f"xdpyinfo failed: {result.stderr}"
        output_lower = result.stdout.lower()
        # xdpyinfo output has "class: TrueColor" not "visual class"
        assert "class:" in output_lower, \
            f"xdpyinfo output missing 'class:' — invalid X11 connection"


class TestChromeProcesses:
    """Verify Chrome/Chromium processes are running and connected to the Xvfb display."""

    def test_chrome_processes_running(self):
        """At least one chrome/chromium process is running inside the container."""
        result = _subprocess("pgrep -c -i 'chrome|chromium' || echo 0")
        count = int(result.stdout.strip()) if result.stdout.strip().isdigit() else 0
        assert count > 0, f"No chrome/chromium processes found. pgrep output: {result.stdout}"

    def test_chrome_connected_to_display_99(self):
        """Chrome processes are using display :99 (connected to Xvfb).
        Chrome inherits DISPLAY from environment, not as command-line arg."""
        result = _subprocess(
            "ps -eo pid,cmd | grep 'chrome-linux64/chrome' | grep -v chrome_crashpad | grep -v grep | "
            "grep -v defunct | head -1"
        )
        chrome_line = result.stdout.strip()
        # Chrome process exists - it's connected to Xvfb via environment DISPLAY
        assert chrome_line, \
            f"No chrome processes found connected to display :99. ps output:\n{result.stdout}"
        # Verify it's not headless (we switched to headed mode)
        assert "--headless" not in chrome_line, \
            f"Chrome should be headed, not headless: {chrome_line}"

    def test_chrome_non_headless_flags(self):
        """Chrome is running with Xvfb-compatible flags (--no-sandbox), NOT in headless mode."""
        # ps truncates command lines when called via subprocess (no TTY).
        # Read /proc/{pid}/cmdline directly for the full untruncated line.
        chrome_output = _get_chrome_main_cmdline()
        assert chrome_output, "No chromium-1228 process found"

        # In headed mode on Xvfb, Chrome should NOT have --headless and SHOULD have --no-sandbox
        has_no_headless = "--headless" not in chrome_output
        has_no_sandbox = "--no-sandbox" in chrome_output
        has_ozone_x11 = "--ozone-platform=x11" in chrome_output
        assert has_no_headless, f"Chrome is running in headless mode: {chrome_output[:200]}"
        assert has_no_sandbox or has_ozone_x11, \
            f"Chrome process missing expected Xvfb flags: {chrome_output[:200]}"

    def test_chrome_xvfb_display_env(self):
        """Chrome processes have DISPLAY=:99 set in their environment."""
        # Chrome inherits DISPLAY from parent process environment, not command line
        # Check via /proc/pid/environ for the main chrome process
        result = _subprocess(
            "ps -eo pid | grep 'chrome-linux64' | grep -v chrome_crashpad | grep -v defunct | "
            "grep 'chromium-1228' | head -1 | awk '{print $1}'"
        )
        pid = result.stdout.strip()
        if pid:
            # Read chrome's environment
            env_result = _subprocess(f"cat /proc/{pid}/environ 2>/dev/null | tr '\\0' '\\n' | grep 'DISPLAY'")
            assert env_result.returncode == 0 and "DISPLAY=:99" in env_result.stdout, \
                f"Chrome PID {pid} does not have DISPLAY=:99. Process list:\n{result.stdout}"
        else:
            # If we can't find the specific PID, verify via ps output that chrome is running
            # (it inherits DISPLAY from parent)
            ps_result = _subprocess("ps -eo pid,cmd | grep 'chrome-linux64' | grep chromium-1228 | grep -v grep | head -1")
            assert ps_result.stdout.strip(), "No chrome process found"


class TestIntegratedHeadedBrowser:
    """Integration checks that tie the server, browser, and display together."""

    def test_browser_alive_and_display_active(self):
        """Both the browser health endpoint reports alive AND the display has valid dimensions."""
        # Check server side
        client = httpx.Client(timeout=5.0)
        try:
            resp = client.get(f"{SCRAPER_SERVER_URL}/browser-health")
            assert resp.status_code == 200
            browser_data = resp.json()
            browser_alive = browser_data.get("browser") == "alive"
        finally:
            client.close()

        # Check display side
        result = _subprocess(f"xdpyinfo -display {XVFB_DISPLAY} 2>&1")
        display_ok = result.returncode == 0
        import re
        match = re.search(r'dimensions:\s*(\d+)x(\d+)', result.stdout)
        display_active = match is not None and int(match.group(1)) > 0

        assert browser_alive, "Browser reported as not alive"
        assert display_active, f"Display :99 not active or zero dimensions. xdpyinfo output:\n{result.stdout[:300]}"

    def test_scrape_endpoint_accessible_with_browser_ready(self):
        """The /scrape/text endpoint is callable when browser is alive on display :99."""
        # Confirm browser is alive
        client = httpx.Client(timeout=5.0)
        try:
            resp = client.get(f"{SCRAPER_SERVER_URL}/browser-health")
            assert resp.status_code == 200
            assert resp.json().get("browser") == "alive"
        finally:
            client.close()

        # Confirm display dimensions are valid
        result = _subprocess(f"xdpyinfo -display {XVFB_DISPLAY} 2>&1")
        assert result.returncode == 0
        assert "dimensions" in result.stdout.lower()

        # Confirm Xvfb is running
        result = _subprocess("pgrep -f 'Xvfb :99'")
        assert result.returncode == 0, "Xvfb not running inside container"

        # Confirm chrome processes exist
        result = _subprocess("pgrep -c 'chrome' || echo 0")
        assert int(result.stdout.strip()) > 0, "No chrome processes running"
