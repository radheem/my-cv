# cv-tailor ingest runtime — headed Chromium under Xvfb, with x11vnc for human-in-the-loop.
# The Playwright base image ships Chromium + all OS deps; we add the virtual display + VNC.
# noble = Ubuntu 24.04 / Python 3.12 (the project requires >=3.11); version matches the
# pip-installed playwright so the bundled browser is correct.
FROM mcr.microsoft.com/playwright/python:v1.60.0-noble

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
    && apt-get install -y --no-install-recommends xvfb x11vnc x11-utils tini \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install deps first for layer caching. Browser is already in the base image.
COPY pyproject.toml README.md ./
COPY engine ./engine
RUN pip install --no-cache-dir -e '.[fetch,generate,ollama]' \
    && playwright install chromium

# Persona data (John Doe sample); mounted read-only at runtime, copied for standalone runs.
COPY data ./data
# doc.css for plain PDF rendering (engine/documents.py); rest of docs/ stays out of the image.
COPY docs/assets ./docs/assets

COPY docker/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Search config is NOT baked in (note: no `COPY config`). It is mounted at runtime at
# the path below so it can be edited without rebuilding the image.
ENV DISPLAY=:99 \
    LINKEDIN_USER_DATA_DIR=/app/vault/profile \
    CV_TAILOR_VAULT=/app/vault \
    CV_TAILOR_SEARCH_CONFIG=/app/config/search.yml \
    SCREEN_GEOMETRY=1440x900x24

# tini reaps Xvfb/x11vnc children cleanly.
ENTRYPOINT ["tini", "--", "/usr/local/bin/entrypoint.sh"]
# Default: run every search in the mounted config/search.yml.
CMD ["cv-tailor", "hunt"]
