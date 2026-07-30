# Implementation Plan: Playwright Scraper Endpoint

## Phase 1: Browser Pool Module

- [ ] Task: Write tests for the browser pool module
    - [ ] Write test that `get_browser()` returns a connected browser handle
    - [ ] Write test that the pool auto-starts on first access
    - [ ] Write test that a crashed browser is detected and relaunched
    - [ ] Write test that `get_browser()` is thread-safe
- [ ] Task: Implement the browser pool (`engine/scrapers.py`)
    - [ ] Create `_BrowserPool` class with background process launcher
    - [ ] Implement `get_browser()` with thread-safe access and auto-start
    - [ ] Implement crash detection via `browser.is_connected()` polling
    - [ ] Implement auto-relaunch on disconnect
    - [ ] Run tests and confirm they pass
- [ ] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md)

## Phase 2: FastAPI Endpoints

- [ ] Task: Write tests for the HTTP endpoints
    - [ ] Write test that `GET /health` returns 200 `{"status": "ok"}`
    - [ ] Write test that `GET /browser-health` returns browser status
    - [ ] Write test that `GET /scrape/text?url=<valid>` returns page text
    - [ ] Write test that `GET /scrape/text?url=<invalid>` returns error
    - [ ] Write test that separate requests use isolated contexts
- [ ] Task: Implement the FastAPI app (`engine/scraper_server.py`)
    - [ ] Create FastAPI app with `/health` route
    - [ ] Create `/browser-health` route checking browser pool state
    - [ ] Create `/scrape/text` route with stealth, timeout, fresh context
    - [ ] Wire browser pool into the app startup lifecycle
    - [ ] Add shutdown handler to close browser
    - [ ] Run tests and confirm they pass
- [ ] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)

## Phase 3: Docker Integration & MCP Routing

- [ ] Task: Write integration tests
    - [ ] Write test that the server starts and serves `/health` inside container
    - [ ] Write test that `fetch_indeed_job` routes through container when available
    - [ ] Write test that host-side fallback works when container unreachable
- [ ] Task: Integrate into Docker setup
    - [ ] Add `engine/scraper_server.py` to the Docker image entrypoint
    - [ ] Expose the scrapers port in docker-compose.yml (port 8000)
    - [ ] Wire scrapers startup into entrypoint.sh (launch server alongside Xvfb)
- [ ] Task: Route MCP tools through the container
    - [ ] Add `_container_scrape(url)` helper to MCP tool layer
    - [ ] Update `fetch_indeed_job` to try container scrape on direct API failure
    - [ ] Add retry logic with configurable timeout
    - [ ] Run integration tests and confirm they pass
- [ ] Task: Conductor - User Manual Verification 'Phase 3' (Protocol in workflow.md)

## Phase 4: End-to-End Testing

- [ ] Task: E2E verification
    - [ ] Clean start: `docker compose down -v && docker compose up -d db mcp ingest`
    - [ ] Verify `/health` and `/browser-health` endpoints
    - [ ] Scrape a live Indeed job and confirm full text is returned
    - [ ] Run full test suite: `uv run pytest -v`
    - [ ] Run MCP E2E client tests: `uv run pytest -v tests/test_mcp_e2e_client.py`
- [ ] Task: Conductor - User Manual Verification 'Phase 4' (Protocol in workflow.md)
