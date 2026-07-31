# Implementation Plan: Scraper & Login Startup Control

- **Track ID:** `manage_scraper_and_login_20260719`
- **Type:** Feature
- **Status:** Planning

---

## Phase 1: Session Controller Refactoring (TDD)

### Task 1.1: Write Failing Tests for `LOGIN_ON_START` (Red Phase)
- [x] Create `tests/test_startup_control.py` to test session login behavior.
- [x] Implement `test_login_on_start_false_warm_session` to verify that when `LOGIN_ON_START=false` and a session is already authenticated, it proceeds with no login attempt.
- [x] Implement `test_login_on_start_false_cold_session_timeout` to verify that when `LOGIN_ON_START=false` and a session is cold, it polls and exits gracefully after the 5-minute timeout.
- [x] Verify that these tests fail as expected against the current codebase.

### Task 1.2: Implement `LOGIN_ON_START` Control in Session Controller (Green Phase)
- [x] Update `engine/domains/linkedin/session.py` to inspect `LOGIN_ON_START` (defaulting to `"true"`).
- [x] Add the time-bounded manual login polling loop (max 300s, polling every 5s) inside `ensure_logged_in()`.
- [x] Implement structured JSON logging during the manual login polling and timeout phase.
- [x] Verify that all unit tests pass.

### Task 1.3: Conductor - User Manual Verification 'Phase 1: Session Controller Refactoring' (Protocol in workflow.md)
- [x] Run the complete test suite (`uv run --no-sync python3 -m pytest`) and verify that all 184+ tests pass.

---

## Phase 2: Container Entrypoint & Docker Configuration

### Task 2.1: Write Bash Tests or Verify Entrypoint Intercepts
- [x] Mock the entrypoint logic to assert that `SCRAPE_JOBS=false` prevents execution of `cv-tailor hunt`.

### Task 2.2: Implement `SCRAPE_JOBS` Intercept in Entrypoint
- [x] Update `docker/entrypoint.sh` to check `SCRAPE_JOBS` (defaulting to `"false"` if undefined).
- [x] Add the blocking loop (`exec sleep infinity`) when `cv-tailor hunt` is skipped or when the Python script exits gracefully due to a manual login timeout.
- [x] Update `.env.example` to document `SCRAPE_JOBS` and `LOGIN_ON_START`.

### Task 2.3: Conductor - User Manual Verification 'Phase 2: Container Entrypoint' (Protocol in workflow.md)
- [x] Build and verify container startup behavior locally using docker compose configurations.

---

## Phase 3: Documentation

### Task 3.1: Add Setup Runbook Documentation
- [x] Document the new parameters, how to connect via VNC, and manual startup triggers inside `docs/setup.md`.

### Task 3.2: Conductor - User Manual Verification 'Phase 3: Documentation' (Protocol in workflow.md)
- [x] Confirm documentation accuracy and finalize the track.
