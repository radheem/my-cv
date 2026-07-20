#!/usr/bin/env bash
# Start a virtual display + VNC, then exec the command (default: cv-tailor hunt).
set -euo pipefail

: "${DISPLAY:=:99}"
: "${SCREEN_GEOMETRY:=1440x900x24}"

Xvfb "$DISPLAY" -screen 0 "$SCREEN_GEOMETRY" >/tmp/xvfb.log 2>&1 &
# Wait for the display to come up (x11-utils provides xdpyinfo).
for _ in $(seq 1 50); do
  if xdpyinfo -display "$DISPLAY" >/dev/null 2>&1; then break; fi
  sleep 0.2
done

# x11vnc: a human attaches here (mapped to 127.0.0.1:5900 by compose) to solve OTP/CAPTCHA.
# Password-protect only if VNC_PASSWORD is set; otherwise rely on the localhost-only mapping.
if [ -n "${VNC_PASSWORD:-}" ]; then
  x11vnc -display "$DISPLAY" -forever -shared -rfbport 5900 -passwd "$VNC_PASSWORD"     >/tmp/x11vnc.log 2>&1 &
else
  x11vnc -display "$DISPLAY" -forever -shared -rfbport 5900 -nopw >/tmp/x11vnc.log 2>&1 &
fi

# Intercept cv-tailor hunt if SCRAPE_JOBS is not set to true
if [ "${SCRAPE_JOBS:-false}" != "true" ] && [ "${SCRAPE_JOBS:-false}" != "1" ] && [ "${SCRAPE_JOBS:-false}" != "yes" ]; then
  if [ "$#" -ge 2 ] && [ "$1" = "cv-tailor" ] && [ "$2" = "hunt" ]; then
    echo "========================================================================"
    echo "SCRAPE_JOBS is set to false (or not set to true)."
    echo "Auto-crawler (hunt) skipped on startup. Keeping container alive..."
    echo "Connect to VNC on port 5900 to perform any manual login flows,"
    echo "or run the crawl manually with:"
    echo "  docker compose exec -it ingest cv-tailor hunt"
    echo "========================================================================"
    exec sleep infinity
  fi
fi

# Run the command and capture its exit status
set +e
"$@"
status=$?
set -e

# If the hunt command exits or fails (e.g. timeout), keep the container alive for VNC investigation
if [ "$#" -ge 2 ] && [ "$1" = "cv-tailor" ] && [ "$2" = "hunt" ]; then
  if [ "$status" -ne 0 ]; then
    echo "========================================================================"
    echo "The hunt crawler exited (status $status). Keeping container alive..."
    echo "========================================================================"
    exec sleep infinity
  fi
fi

exit "$status"
