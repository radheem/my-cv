"""LinkedIn session: persistent context + human-paced credentialed login.

The only module that authenticates. Credentials are read from the environment
(`LINKEDIN_USER` / `LINKEDIN_PASS`, loaded from `.env`) inside `_login` and typed straight
into the field — never passed as arguments, never returned, never logged.

Challenge handling (decisions D2/D5):
  - OTP   → `resolver.request_otp(screenshot)` returns a code we type in.
  - CAPTCHA / unknown checkpoint → `resolver.wait_for_human(...)`; a human solves it live
    (via VNC) while we poll for the logged-in state.

`with_session(action)` runs an action and, if it trips on a logged-out state mid-flow,
re-logs-in once and retries.
"""

from __future__ import annotations

import logging
import os
import pathlib
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable, Protocol

from .humanize import human_click, human_pause, human_type, settle

log = logging.getLogger("cv_tailor.linkedin")

FEED_URL = "https://www.linkedin.com/feed/"
LOGIN_URL = "https://www.linkedin.com/login"


class ChallengeTimeout(RuntimeError):
    """A human challenge (OTP/CAPTCHA) was not resolved in time."""


class PageState(Enum):
    LOGGED_IN = auto()
    LOGIN = auto()
    CHALLENGE_OTP = auto()
    CHALLENGE_CAPTCHA = auto()
    UNKNOWN = auto()


_CAPTCHA_MARKERS = (
    "captcha",
    "recaptcha",
    "are you a human",
    "security check",
    "verify you're a human",
    "let's do a quick security check",
    "px-captcha",
)
_OTP_MARKERS = (
    "verification code",
    "enter the code",
    "two-step verification",
    "one-time",
    "we sent a code",
    "pin",
)
_LOGIN_MARKERS = ('name="session_key"', 'id="username"', 'action="/checkpoint/lg/login-submit"')
_FEED_MARKERS = (
    "/feed",
    'id="global-nav"',
    'class="global-nav',
    "feed-identity-module",
    'data-control-name="identity_welcome_message"',
)


def classify_page(url: str, html: str) -> PageState:
    """Best-effort page classification from URL + HTML. Pure (unit-tested)."""
    u = (url or "").lower()
    h = (html or "").lower()

    if "checkpoint" in u or "/checkpoint/" in u:
        if any(m in h for m in _CAPTCHA_MARKERS):
            return PageState.CHALLENGE_CAPTCHA
        if any(m in h for m in _OTP_MARKERS):
            return PageState.CHALLENGE_OTP
        return PageState.CHALLENGE_CAPTCHA  # unknown checkpoint → treat as human-required

    if "/login" in u or "/uas/login" in u or any(m in h for m in _LOGIN_MARKERS):
        # a fully logged-in feed page won't carry the login form markers
        if not (u.endswith("/feed/") or "/feed/" in u):
            return PageState.LOGIN

    if any(m in u or m in h for m in _FEED_MARKERS):
        return PageState.LOGGED_IN

    return PageState.UNKNOWN


# ── challenge resolvers ─────────────────────────────────────────────────────────────────


class ChallengeResolver(Protocol):
    def request_otp(self, screenshot_path: str) -> str: ...

    def wait_for_human(
        self, screenshot_path: str, reason: str, is_resolved: Callable[[], bool], timeout: float
    ) -> bool: ...


class StdinResolver:
    """Interactive resolver — prompts on the terminal. Used when a TTY is attached."""

    def request_otp(self, screenshot_path: str) -> str:
        print(
            f"\n[LinkedIn] One-time code required. Screenshot: {screenshot_path}",
            flush=True,
        )
        return input("Enter the verification code: ").strip()

    def wait_for_human(self, screenshot_path, reason, is_resolved, timeout) -> bool:
        print(
            f"\n[LinkedIn] {reason}. Solve it in the live browser (VNC). "
            f"Screenshot: {screenshot_path}",
            flush=True,
        )
        input("Press Enter once you've completed it… ")
        return is_resolved()


class FileInboxResolver:
    """Detached resolver — writes a request + screenshot to vault/challenges/ and polls for
    a response file. Used when no TTY is attached (cron / detached docker run)."""

    def __init__(self, inbox: pathlib.Path, poll: float = 3.0, timeout: float = 300.0):
        self.inbox = pathlib.Path(inbox)
        self.inbox.mkdir(parents=True, exist_ok=True)
        self.poll = poll
        self.timeout = timeout

    def request_otp(self, screenshot_path: str) -> str:
        req = self.inbox / "otp-request.txt"
        resp = self.inbox / "otp-response.txt"
        resp.unlink(missing_ok=True)
        req.write_text(f"OTP needed. Screenshot: {screenshot_path}\nWrite the code to {resp}\n")
        deadline = time.time() + self.timeout
        while time.time() < deadline:
            if resp.exists():
                code = resp.read_text().strip()
                resp.unlink(missing_ok=True)
                req.unlink(missing_ok=True)
                return code
            time.sleep(self.poll)
        raise ChallengeTimeout(f"no OTP response in {self.timeout:.0f}s ({resp})")

    def wait_for_human(self, screenshot_path, reason, is_resolved, timeout) -> bool:
        req = self.inbox / "captcha-request.txt"
        req.write_text(
            f"{reason}. Connect via VNC (127.0.0.1:5900) and solve it.\n"
            f"Screenshot: {screenshot_path}\n"
        )
        deadline = time.time() + min(timeout, self.timeout)
        while time.time() < deadline:
            if is_resolved():
                req.unlink(missing_ok=True)
                return True
            time.sleep(self.poll)
        return False


# ── session ─────────────────────────────────────────────────────────────────────────────


@dataclass
class LinkedInSession:
    user_data_dir: str
    vault_dir: str
    resolver: ChallengeResolver
    headless: bool = False
    challenge_timeout: float = 300.0
    _ctx: object = field(default=None, repr=False)

    @property
    def challenges_dir(self) -> pathlib.Path:
        d = pathlib.Path(self.vault_dir) / "challenges"
        d.mkdir(parents=True, exist_ok=True)
        return d

    def context(self, playwright):
        """Launch a persistent, headed context (recognized-device profile, decisions D1)."""
        user_data_path = pathlib.Path(self.user_data_dir)
        user_data_path.mkdir(parents=True, exist_ok=True)
        
        # Remove any stale Chromium singleton lock to prevent TargetClosedError
        lock_file = user_data_path / "SingletonLock"
        if lock_file.exists() or lock_file.is_symlink():
            try:
                lock_file.unlink(missing_ok=True)
                log.info(f"Removed stale Chromium singleton lock file: {lock_file}")
            except Exception as e:
                log.warning(f"Failed to remove singleton lock file {lock_file}: {e}")

        self._ctx = playwright.chromium.launch_persistent_context(
            self.user_data_dir,
            headless=self.headless,
            locale="en-US",
            timezone_id="UTC",
            viewport={"width": 1440, "height": 900},
            user_agent=(
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            args=["--disable-blink-features=AutomationControlled"],
        )
        return self._ctx

    def page(self):
        pages = self._ctx.pages
        page = pages[0] if pages else self._ctx.new_page()
        try:
            from playwright_stealth import stealth_sync
            stealth_sync(page)
        except ImportError:
            pass
        return page

    def close(self) -> None:
        if self._ctx is not None:
            self._ctx.close()
            self._ctx = None

    # ── login ──────────────────────────────────────────────────────────────────────────

    def ensure_logged_in(self, page) -> None:
        page.goto(FEED_URL, wait_until="domcontentloaded")
        settle(page)
        if classify_page(page.url, page.content()) == PageState.LOGGED_IN:
            log.info("already authenticated (warm profile)")
            return

        login_on_start = os.environ.get("LOGIN_ON_START", "true").lower() in ("true", "1", "yes")
        if not login_on_start:
            import json
            log.warning("Not authenticated on LinkedIn, and LOGIN_ON_START is set to false.")
            log.warning("Bypassing automated credential login. Please connect to VNC (port 5900) and log in manually.")
            log.warning(json.dumps({"event": "manual_login_wait", "status": "waiting_on_vnc"}))
            print("\n⏰ Waiting for manual login via VNC viewer... Press Ctrl+C to cancel.\n", flush=True)
            
            timeout = 300  # 5 minutes
            interval = 5
            elapsed = 0
            authenticated = False
            
            while elapsed < timeout:
                page.goto(FEED_URL, wait_until="domcontentloaded")
                settle(page)
                if classify_page(page.url, page.content()) == PageState.LOGGED_IN:
                    authenticated = True
                    break
                time.sleep(interval)
                elapsed += interval
                
            if not authenticated:
                log.error(json.dumps({"event": "manual_login_timeout", "status": "failed"}))
                raise SystemExit("Manual login timed out. LOGIN_ON_START is false and no manual login was detected within 300 seconds.")
                
            log.info("Authenticated successfully via manual VNC login!")
            return

        self._login(page)

    def _login(self, page) -> None:
        user = os.environ.get("LINKEDIN_USER")
        password = os.environ.get("LINKEDIN_PASS")
        if not user or not password:
            raise RuntimeError("LINKEDIN_USER / LINKEDIN_PASS not set (put them in .env)")
        log.info("starting human-paced credentialed login")
        page.goto(LOGIN_URL, wait_until="domcontentloaded")
        settle(page)
        self._dump(page, "login-page")  # diagnostic: what did LinkedIn actually serve?

        state = classify_page(page.url, page.content())
        if state in (PageState.CHALLENGE_OTP, PageState.CHALLENGE_CAPTCHA):
            log.warning("challenge presented before the login form (%s)", state.name)
            self._await_login(page)
            return

        # LinkedIn's current login is a React page: no #username/session_key, fields keyed by
        # autocomplete, with duplicate hidden inputs — so match by attribute and pick the
        # VISIBLE instance.
        user_loc = self._first_visible(
            page, ("input[autocomplete='username']", "input[type='email']", "#username")
        )
        pass_loc = self._first_visible(
            page,
            ("input[autocomplete='current-password']", "input[type='password']", "#password"),
        )
        if user_loc is None or pass_loc is None:
            self._dump(page, "login-no-fields")
            raise RuntimeError(f"login fields not found (state={state.name}, url={page.url})")

        human_type(page, user_loc, user)
        human_pause(0.5, 1.4)
        human_type(page, pass_loc, password)
        human_pause(0.6, 1.6)
        page.keyboard.press("Enter")  # focus is in the password field; Enter submits
        self._await_login(page)

    def _first_visible(self, page, selectors, timeout_ms: int = 6000):
        """Poll selectors and return the first VISIBLE matching element, or None."""
        deadline = time.time() + timeout_ms / 1000
        while time.time() < deadline:
            for sel in selectors:
                loc = page.locator(sel)
                for i in range(loc.count()):
                    cand = loc.nth(i)
                    try:
                        if cand.is_visible():
                            return cand
                    except Exception:
                        continue
            time.sleep(0.25)
        return None

    def _dump(self, page, kind: str) -> str:
        """Screenshot + HTML dump to vault/challenges/ for diagnosis."""
        shot = self._screenshot(page, kind)
        try:
            (self.challenges_dir / f"{kind}.html").write_text(page.content(), encoding="utf-8")
        except Exception as e:
            log.debug("html dump failed: %s", e)
        log.info("captured %s (url=%s)", kind, page.url)
        return shot

    def _await_login(self, page, attempts: int = 5) -> None:
        for _ in range(attempts):
            settle(page, 2.0, 3.5)
            state = classify_page(page.url, page.content())
            if state == PageState.LOGGED_IN:
                log.info("login successful")
                return
            if state == PageState.CHALLENGE_OTP:
                shot = self._dump(page, "otp")
                log.warning("OTP challenge — requesting code")
                self._submit_otp(page, self.resolver.request_otp(shot))
                continue
            if state == PageState.CHALLENGE_CAPTCHA:
                shot = self._dump(page, "captcha")
                log.warning("CAPTCHA / security checkpoint — handing off to human")
                ok = self.resolver.wait_for_human(
                    shot,
                    "CAPTCHA / security check",
                    lambda: classify_page(page.url, page.content()) == PageState.LOGGED_IN,
                    self.challenge_timeout,
                )
                if ok:
                    log.info("challenge resolved by human")
                    return
                continue
            if state == PageState.LOGIN:
                self._dump(page, "login-failed")
                raise RuntimeError("still on the login page after submit — check credentials")
        raise ChallengeTimeout("could not reach a logged-in state")

    def _submit_otp(self, page, code: str) -> None:
        selectors = (
            "input[name=pin]",
            "input#input__email_verification_pin",
            "input[autocomplete=one-time-code]",
            "input[name=verification_code]",
        )
        for sel in selectors:
            loc = page.locator(sel)
            if loc.count():
                human_type(page, loc.first, code)
                human_pause()
                human_click(page, page.locator("button[type=submit]").first)
                return
        page.keyboard.type(code)
        page.keyboard.press("Enter")

    def _screenshot(self, page, kind: str) -> str:
        path = self.challenges_dir / f"{kind}-{int(time.time())}.png"
        try:
            page.screenshot(path=str(path), full_page=False)
        except Exception as e:  # never let a screenshot failure abort the flow
            log.debug("screenshot failed: %s", e)
        return str(path)

    # ── action wrapper ──────────────────────────────────────────────────────────────────

    def with_session(self, action: Callable):
        """Run `action(page)`; if it fails on a logged-out state, relogin once and retry."""
        page = self.page()
        self.ensure_logged_in(page)
        for attempt in (1, 2):
            try:
                return action(page)
            except Exception:
                if attempt == 2:
                    raise
                state = classify_page(page.url, page.content())
                if state == PageState.LOGGED_IN:
                    raise  # a real error, not an auth problem
                log.warning("auth lost mid-flow (%s) — re-logging in and retrying", state.name)
                self.ensure_logged_in(page)
