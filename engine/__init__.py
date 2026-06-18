"""cv-tailor generation engine.

Two halves with a hard boundary:
  - rank.py  : PURE relevance scoring (no I/O, no network) — unit-tested.
  - jobspec.py / render.py : Claude API calls (local only, need ANTHROPIC_API_KEY).
"""

__version__ = "0.1.0"
