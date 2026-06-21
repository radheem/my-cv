#!/usr/bin/env bash
# Start a virtual display + VNC, then exec the command (default: cv-tailor ingest).
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
  x11vnc -display "$DISPLAY" -forever -shared -rfbport 5900 -passwd "$VNC_PASSWORD" \
    >/tmp/x11vnc.log 2>&1 &
else
  x11vnc -display "$DISPLAY" -forever -shared -rfbport 5900 -nopw >/tmp/x11vnc.log 2>&1 &
fi

exec "$@"
