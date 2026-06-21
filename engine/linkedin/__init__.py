"""LinkedIn ingest — drive a logged-in session and capture job descriptions.

Sprint 1 (see sprints/tracks/sprint-1-linkedin-ingest/). Two halves:

- `session` — persistent context, human-paced credentialed login from `.env`, challenge
  handling (OTP prompt / CAPTCHA via VNC), auto-relogin + retry.
- `jobs` — search + clean JD extraction → `vault/jds/<slug>.txt`.

Nothing here submits an application (stop-before-submit, decisions D4).
"""
