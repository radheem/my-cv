import pytest
from engine.workflows import create_application_workflow, update_application_status_workflow, score_jobs_workflow


def test_workflow_error_isolation():
    # Make sure we isolate errors and return clear exception strings instead of crashing
    res = create_application_workflow("invalid_nonexistent_file_path_xyz.txt")
    assert "ERROR" in res


def test_workflow_status_nonexistent():
    res = update_application_status_workflow("nonexistent-slug-123", "applied")
    assert "ERROR" in res
