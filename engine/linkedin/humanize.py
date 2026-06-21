"""Human-paced browser actions — deliberate, jittered timing to look less like a bot.

Every pause routes through `_sleep`, which scales by the `LINKEDIN_PACE` env var
(default 1.0). Set `LINKEDIN_PACE=0` in tests for instant runs; raise it above 1 to slow
down further on a touchy account.
"""

from __future__ import annotations

import os
import random
import time


def _pace() -> float:
    try:
        return float(os.environ.get("LINKEDIN_PACE", "1") or "1")
    except ValueError:
        return 1.0


def _sleep(seconds: float) -> None:
    time.sleep(max(0.0, seconds * _pace()))


def human_pause(lo: float = 0.4, hi: float = 1.8) -> None:
    """Idle for a random beat, the way a person pauses between actions."""
    _sleep(random.uniform(lo, hi))


def settle(page, lo: float = 1.2, hi: float = 2.6) -> None:
    """Wait for the page to quiesce, then a human beat. networkidle on LinkedIn often
    never fires (long-poll sockets), so the wait is best-effort and capped."""
    try:
        page.wait_for_load_state("networkidle", timeout=8000)
    except Exception:
        pass
    human_pause(lo, hi)


def human_type(page, locator, text: str, lo: float = 0.06, hi: float = 0.22) -> None:
    """Focus a field and type one character at a time with per-keystroke jitter and the
    occasional longer hesitation. The text is never logged."""
    locator.click()
    human_pause(0.15, 0.5)
    for ch in text:
        page.keyboard.type(ch)
        _sleep(random.uniform(lo, hi))
        if random.random() < 0.05:  # occasional think-pause
            _sleep(random.uniform(0.3, 0.9))


def human_click(page, locator) -> None:
    """Scroll a target into view, pause, then click."""
    try:
        locator.scroll_into_view_if_needed(timeout=4000)
    except Exception:
        pass
    human_pause(0.2, 0.7)
    locator.click()


def human_scroll(page, steps: int = 3) -> None:
    """Wheel-scroll in a few jittered increments to trigger lazy loading."""
    for _ in range(steps):
        page.mouse.wheel(0, random.randint(300, 700))
        human_pause(0.4, 1.2)
