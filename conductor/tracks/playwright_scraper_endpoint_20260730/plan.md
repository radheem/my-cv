# Implementation Plan: Playwright Scraper Endpoint

## Phase 1: Browser Pool Module

- [x] Task: Write tests for the browser pool module 7a3b2f1
    - [x] Write test that `get_browser()` returns a connected browser handle
    - [x] Write test that the pool auto-starts on first access
    - [x] Write test that a crashed browser is detected and relaunched
    - [x] Write test that `get_browser()` is thread-safe
- [x] Task: Implement the browser pool (`engine/scrapers.py`)
    - [x] Create `BrowserPool` class with async playwright launcher
    - [x] Implement `get_browser()` with thread-safe access and auto-start
    - [x] Implement crash detection via `browser.is_connected()` polling
    - [x] Implement auto-relaunch on disconnect
    - [x] Run tests and confirm they pass (11/11 passed)
- [x] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md)

### Phase 1 Checkpoint [checkpoint: 7a3b2f1]
```
Phase 1 verification completed. All tests pass. Manual verification confirmed:
- BrowserPool creates Chromium on first access: PASS
- Singleton behavior verified: PASS
- is_alive() / is_alive(after close) verified: PASS
- Dead browser detection and relaunch: PASS
- Module-level get_browser() / stop(): PASS
```

## Phase 2: FastAPI Endpoints

- [x] Task: Write tests for the HTTP endpoints 1b4c5d2
    - [x] Write test that `GET /health` returns 200 `{"status": "ok"}`
    - [x] Write test that `GET /browser-health` returns browser status
    - [x] Write test that `GET /scrape/text?url=<valid>` returns page text
    - [x] Write test that `GET /scrape/text?url=<invalid>` returns error
    - [x] Write test that separate requests use isolated contexts
- [x] Task: Implement the FastAPI app (`engine/scraper_server.py`)
    - [x] Create FastAPI app with `/health` route
    - [x] Create `/browser-health` route checking browser pool state
    - [x] Create `/scrape/text` route with stealth, timeout, fresh context
    - [x] Wire browser pool into the app startup lifecycle
    - [x] Add shutdown handler to close browser
    - [x] Run tests and confirm they pass (11 scrapers + 6 server = 17 total)
- [x] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)

### Phase 2 Checkpoint [checkpoint: 1b4c5d2]
```
Phase 2 verification completed. All 6 server tests pass. Manual verification confirmed:
- /health returns 200 {"status": "ok"}: PASS
- /browser-health returns dead/alive correctly: PASS
- /scrape/text returns page text: PASS
- /scrape/text returns 504 on timeout: PASS
- /scrape/text creates isolated contexts per request: PASS
```

## Phase 3: Docker Integration & MCP Routing

- [x] Task: Write integration tests
    - [x] Write test that the server starts and serves `/health` inside container
    - [x] Write test that `fetch_indeed_job` routes through container when available
    - [x] Write test that host-side fallback works when container unreachable
- [x] Task: Integrate into Docker setup
    - [x] Add `engine/scraper_server.py` to the Docker image entrypoint
    - [x] Expose the scrapers port in docker-compose.yml (port 8000)
    - [x] Wire scrapers startup into entrypoint.sh (launch server alongside Xvfb)
- [x] Task: Route MCP tools through the container
    - [x] Add `_container_scrape(url)` helper to MCP tool layer
    - [x] Update `fetch_indeed_job` to try container scrape on direct API failure
    - [x] Add retry logic with configurable timeout
    - [x] Run integration tests and confirm they pass
- [ ] Task: Conductor - User Manual Verification 'Phase 3' (Protocol in workflow.md)

## Phase 4: End-to-End Testing

- [ ] Task: E2E verification
    - [ ] Clean start: `docker compose down -v && docker compose up -d db mcp ingest`
    - [ ] Verify `/health` and `/browser-health` endpoints
    - [ ] Scrape a live Indeed job and confirm full text is returned
    - [ ] Run full test suite: `uv run pytest -v`
    - [ ] Run MCP E2E client tests: `uv run pytest -v tests/test_mcp_e2e_client.py`
- [ ] Task: Conductor - User Manual Verification 'Phase 4' (Protocol in workflow.md)
