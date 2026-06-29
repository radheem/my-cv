import pathlib
import sys
import pytest
from unittest.mock import patch

# Make the repo root importable so `from engine import rank` works without an
# editable install.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))


@pytest.fixture(autouse=True)
def mock_tailor_workflow():
    """Globally mock the slow application tailoring workflow during tests to prevent queue backups."""
    with patch("engine.mcp.server.create_application_from_job_workflow", return_value="SUCCESS") as mock:
        yield mock

