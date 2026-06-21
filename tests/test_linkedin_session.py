"""Unit tests for engine.linkedin.session — pure page classification, resolver dispatch,
and the load-bearing 'no secret in logs' guard. No browser, no network."""

import logging

import pytest

from engine.linkedin import session as S
from engine.linkedin.session import PageState, classify_page

FEED_HTML = '<html><body><nav id="global-nav">Home</nav><div class="feed-identity-module">'
LOGIN_HTML = '<form><input id="username"><input id="password" name="session_key"></form>'
OTP_HTML = '<html><body>Two-step verification — enter the code we sent</body></html>'
CAPTCHA_HTML = "<html><body>Let's do a quick security check — captcha</body></html>"


@pytest.mark.parametrize(
    "url,html,expected",
    [
        ("https://www.linkedin.com/feed/", FEED_HTML, PageState.LOGGED_IN),
        ("https://www.linkedin.com/login", LOGIN_HTML, PageState.LOGIN),
        ("https://www.linkedin.com/checkpoint/challenge/", OTP_HTML, PageState.CHALLENGE_OTP),
        (
            "https://www.linkedin.com/checkpoint/challenge/",
            CAPTCHA_HTML,
            PageState.CHALLENGE_CAPTCHA,
        ),
        ("https://www.linkedin.com/checkpoint/lg/", "<html>nothing</html>",
         PageState.CHALLENGE_CAPTCHA),  # unknown checkpoint → human
        ("https://example.com/", "<html>random</html>", PageState.UNKNOWN),
    ],
)
def test_classify_page(url, html, expected):
    assert classify_page(url, html) is expected


def test_stdin_resolver_otp(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda *a, **k: "  123456 ")
    code = S.StdinResolver().request_otp("/tmp/shot.png")
    assert code == "123456"
    assert "/tmp/shot.png" in capsys.readouterr().out


def test_file_inbox_resolver_otp(tmp_path):
    resolver = S.FileInboxResolver(tmp_path / "challenges", poll=0.01, timeout=0.05)
    with pytest.raises(S.ChallengeTimeout):
        resolver.request_otp("/tmp/shot.png")  # no response file → times out


# ── no secret in logs ────────────────────────────────────────────────────────────────────

SENTINEL_USER = "user@example.com"
SENTINEL_PASS = "S3nt1nel-P@ssw0rd-DO-NOT-LOG"


class _FakeLocator:
    def count(self):
        return 1

    def nth(self, i):
        return self

    def is_visible(self):
        return True

    @property
    def first(self):
        return self

    def click(self):
        pass

    def scroll_into_view_if_needed(self, *a, **k):
        pass


class _FakeKeyboard:
    def type(self, *a, **k):
        pass

    def press(self, *a, **k):
        pass


class _FakePage:
    """Minimal page stub: lands logged-in immediately so _login completes with no challenge."""

    def __init__(self):
        self.url = "https://www.linkedin.com/feed/"
        self.keyboard = _FakeKeyboard()

    def goto(self, *a, **k):
        pass

    def locator(self, *a, **k):
        return _FakeLocator()

    def content(self):
        return FEED_HTML

    def wait_for_load_state(self, *a, **k):
        pass

    def screenshot(self, *a, **k):
        pass


def test_login_never_logs_the_password(monkeypatch, caplog):
    monkeypatch.setenv("LINKEDIN_USER", SENTINEL_USER)
    monkeypatch.setenv("LINKEDIN_PASS", SENTINEL_PASS)
    monkeypatch.setenv("LINKEDIN_PACE", "0")  # instant pacing

    sess = S.LinkedInSession(user_data_dir="/tmp/x", vault_dir="/tmp/x", resolver=S.StdinResolver())
    with caplog.at_level(logging.DEBUG, logger="cv_tailor.linkedin"):
        sess._login(_FakePage())  # FakePage reports logged-in → returns cleanly

    assert SENTINEL_PASS not in caplog.text
    assert SENTINEL_USER not in caplog.text


def test_login_requires_credentials(monkeypatch):
    monkeypatch.delenv("LINKEDIN_USER", raising=False)
    monkeypatch.delenv("LINKEDIN_PASS", raising=False)
    sess = S.LinkedInSession(user_data_dir="/tmp/x", vault_dir="/tmp/x", resolver=S.StdinResolver())
    with pytest.raises(RuntimeError, match="LINKEDIN_USER"):
        sess._login(_FakePage())
