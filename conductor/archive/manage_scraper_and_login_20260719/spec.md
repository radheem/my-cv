# Specification: Scraper & Login Startup Control

- **Track ID:** `manage_scraper_and_login_20260719`
- **Type:** Feature / Improvement
- **Status:** Planning

---

## 1. Overview
This track adds highly granular controls over the active background crawler (`cv-tailor hunt`) and automated LinkedIn login procedures during container deployment. By utilizing `.env` parameters (`SCRAPE_JOBS` and `LOGIN_ON_START`), users can prevent unauthenticated login triggers on touchy accounts, skip startup crawls entirely, and perform manual warming/OTP solutions safely via VNC without container crashes.

---

## 2. Functional Requirements

### 2.1 Startup Scraper Control (`SCRAPE_JOBS`)
- **Variable:** `SCRAPE_JOBS`
- **Default:** `false` (If missing, undefined, or empty in `.env`).
- **Behavior:**
  - **`true`:** Automatically starts the `cv-tailor hunt` crawl on container boot (retaining current behavior).
  - **`false`:** Intercepts and blocks the auto-hunt command in the container entrypoint (`docker/entrypoint.sh`), printing a clear message and transitioning to an idle sleep (`sleep infinity`) to keep the container running for manual triggers.

### 2.2 Automated Login Override (`LOGIN_ON_START`)
- **Variable:** `LOGIN_ON_START`
- **Default:** `true` (Automated credential login attempts run on boot).
- **Behavior:**
  - **`true`:** Automates credential-typing for cold sessions (standard behavior).
  - **`false`:** If the browser profile is warm/authenticated, proceeds with the crawl. If the browser profile is cold/unauthenticated:
    - Bypasses automatic credential typing to avoid triggering anti-bot alerts.
    - Emits **standard structured JSON logs** flagging that it is waiting for manual user login.
    - Enters a polling loop that navigates to the LinkedIn Feed and checks authentication state.
    - **Timeout:** If manual VNC login is completed within **5 minutes (300 seconds)**, the script logs successful authentication and proceeds with the crawl. If 5 minutes pass without login, the Python script exits gracefully with a structured warning log, and the container entrypoint intercepts this to transition to a safe idle sleep (`sleep infinity`) to keep the container alive.

---

## 3. Technical Requirements & Architecture

### 3.1 Entrypoint Integration (`docker/entrypoint.sh`)
- Overhaul `docker/entrypoint.sh` to check `SCRAPE_JOBS` before invoking `exec ""`.
- Catch Python script exits caused by a manual login timeout and keep the container alive instead of crashing.

### 3.2 Session Controller (`engine/domains/linkedin/session.py`)
- Read `LOGIN_ON_START` within `ensure_logged_in()`.
- Add a structured, time-bounded polling loop (polling every 5 seconds, max 300 seconds total) that monitors browser state to resume crawls as soon as the user finishes manual login in VNC.
- Implement structured JSON logging matching the existing logging format.

---

## 4. Verification and Testing

- **Mock-Based Unit Tests:**
  - Implement pytest unit tests in `tests/` that mock the `os.environ` settings for `SCRAPE_JOBS` and `LOGIN_ON_START`.
  - Assert that the session controller accurately detects authentication state, skips `_login()` when `LOGIN_ON_START=false`, and exits gracefully upon a 5-minute timeout.
- **Runbook Documentation:**
  - Document the parameters, startup logs, and manual VNC login instructions inside `docs/setup.md` or a dedicated setup runbook.
