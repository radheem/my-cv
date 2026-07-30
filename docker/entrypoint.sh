#!/usr/bin/env bash
# Start a virtual display + VNC, then exec the command (default: cv-tailor hunt).
# Runs as root, chown's all mounted volumes, then gosu-switches to a non-root user.
set -euo pipefail

: "${DISPLAY:=:99}"
: "${SCREEN_GEOMETRY:=1440x900x24}"
: "${DOCKER_UID:=1000}"
: "${DOCKER_GID:=1000}"
: "${APP_USER:=cvuser}"

# Create the app user/group matching the desired UID/GID (idempotent)
if ! id "$APP_USER" &>/dev/null; then
  groupadd -g "$DOCKER_GID" "$APP_USER"
  useradd -m -u "$DOCKER_UID" -g "$DOCKER_GID" -s /bin/false "$APP_USER"
fi

# Only chown writable volumes (vault, applications, engine).
# /app/data and /app/config are mounted :read-only — skip them entirely.
VOL_DIRS=(
  /app/vault
  /app/applications
  /app/engine
)
for d in "${VOL_DIRS[@]}"; do
  if [ -d "$d" ]; then
    chown -R "$APP_USER:$APP_USER" "$d" 2>/dev/null || true
  fi
done

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

# Scraper FastAPI server — runs as the app (non-root) user.
# Exposed on port 8000; reachable from outside via host.docker.internal:8000
# or from MCP container via localhost:8000 (since both share the same bridge network).
if [ "${START_SCRAPER_SERVER:-true}" = "true" ]; then
  PYTHONPATH=/app uvicorn engine.scraper_server:app --host 0.0.0.0 --port 8000 \
    >/tmp/scraper.log 2>&1 &
  echo "Scraper server started in background (PID=$!)"
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
    # sleep continues running as root (background processes remain up)
    exec sleep infinity
  fi
fi

# Run the actual command as the non-root user via gosu
# gosu reaps children cleanly like tini; no need for both.
set -- gosu "$APP_USER" "$@"
exec "$@"
