"""Unit tests for SCRAPE_JOBS and LOGIN_ON_START startup controls."""

import logging
import pytest
import time
import sys

from engine.domains.linkedin import session as S
from engine.domains.linkedin.session import PageState

FEED_HTML = '<html><body><nav id="global-nav">Home</nav><div class="feed-identity-module">'
LOGIN_HTML = '<form><input id="username"><input id="password" name="session_key"></form>'

class _FakePage:
    def __init__(self, contents_sequence):
        self.contents = contents_sequence
        self.index = -1

    @property
    def url(self):
        idx = max(0, self.index)
        content = self.contents[idx]
        if 'global-nav' in content:
            return 'https://www.linkedin.com/feed/'
        return 'https://www.linkedin.com/login'

    def goto(self, *a, **k):
        if self.index < len(self.contents) - 1:
            self.index += 1

    def content(self):
        idx = max(0, self.index)
        return self.contents[idx]

def test_login_on_start_false_warm_session(monkeypatch, caplog):
    monkeypatch.setenv("LOGIN_ON_START", "false")
    # Session is already warm (FEED_HTML returned immediately)
    page = _FakePage([FEED_HTML])
    sess = S.LinkedInSession(user_data_dir="/tmp/x", vault_dir="/tmp/x", resolver=S.StdinResolver())
    
    with caplog.at_level(logging.DEBUG, logger="cv_tailor.linkedin"):
        sess.ensure_logged_in(page)
        
    assert "already authenticated" in caplog.text

def test_login_on_start_false_cold_session_and_successful_manual_login(monkeypatch, caplog):
    monkeypatch.setenv("LOGIN_ON_START", "false")
    monkeypatch.setattr(time, "sleep", lambda x: None)
    
    # 2 attempts of LOGIN_HTML, then FEED_HTML on 3rd attempt
    page = _FakePage([LOGIN_HTML, LOGIN_HTML, FEED_HTML])
    sess = S.LinkedInSession(user_data_dir="/tmp/x", vault_dir="/tmp/x", resolver=S.StdinResolver())
    
    with caplog.at_level(logging.DEBUG, logger="cv_tailor.linkedin"):
        sess.ensure_logged_in(page)
        
    assert "Authenticated successfully via manual VNC login!" in caplog.text

def test_login_on_start_false_cold_session_timeout(monkeypatch, caplog):
    monkeypatch.setenv("LOGIN_ON_START", "false")
    monkeypatch.setattr(time, "sleep", lambda x: None)
    
    # Continually returns LOGIN_HTML (remains cold)
    page = _FakePage([LOGIN_HTML])
    sess = S.LinkedInSession(user_data_dir="/tmp/x", vault_dir="/tmp/x", resolver=S.StdinResolver())
    
    # Verify that the polling timeout raises SystemExit gracefully
    with pytest.raises(SystemExit, match="Manual login timed out"):
        sess.ensure_logged_in(page)
