import sys
import pathlib
import pytest
from unittest.mock import patch, MagicMock
import importlib.util

def load_script():
    script_path = pathlib.Path(__file__).resolve().parent.parent / "scripts" / "extract-email-urls.py"
    spec = importlib.util.spec_from_file_location("extract_email_urls", str(script_path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

extract_email_urls = load_script()

def test_extract_unseen_urls_success(capsys):
    stdin_data = '[{"messages": [{"body": "Check this job: https://www.linkedin.com/jobs/view/999999/"}]}]'
    
    with patch("sys.stdin.read", return_value=stdin_data), \
         patch.object(extract_email_urls, "load_seen", return_value={}):
        extract_email_urls.main()
        
    captured = capsys.readouterr()
    assert captured.out == "https://www.linkedin.com/jobs/view/999999/\n"
    assert captured.err == ""

def test_extract_filters_seen_urls(capsys):
    stdin_data = '[{"messages": [{"body": "Check this job: https://www.linkedin.com/jobs/view/999999/ and this seen one: https://www.linkedin.com/jobs/view/111111/"}]}]'
    
    # "111111" is already seen
    with patch("sys.stdin.read", return_value=stdin_data), \
         patch.object(extract_email_urls, "load_seen", return_value={"111111": {}}):
        extract_email_urls.main()
        
    captured = capsys.readouterr()
    assert captured.out == "https://www.linkedin.com/jobs/view/999999/\n"
    assert captured.err == ""

def test_extract_deduplicates_found_ids(capsys):
    stdin_data = '[{"messages": [{"body": "Check this job: https://www.linkedin.com/jobs/view/999999/ and again: https://www.linkedin.com/jobs/view/999999/"}]}]'
    
    with patch("sys.stdin.read", return_value=stdin_data), \
         patch.object(extract_email_urls, "load_seen", return_value={}):
        extract_email_urls.main()
        
    captured = capsys.readouterr()
    assert captured.out == "https://www.linkedin.com/jobs/view/999999/\n"
    assert captured.err == ""

def test_extract_invalid_json(capsys):
    stdin_data = 'invalid json'
    
    with patch("sys.stdin.read", return_value=stdin_data), \
         pytest.raises(SystemExit) as exc_info:
        extract_email_urls.main()
        
    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "Error: Invalid JSON from stdin" in captured.err

def test_extract_empty_payload(capsys):
    stdin_data = '   \n  '
    
    with patch("sys.stdin.read", return_value=stdin_data):
        extract_email_urls.main()
        
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""
