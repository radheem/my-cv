import pathlib
import sys

# Make the repo root importable so `from engine import rank` works without an
# editable install.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
