"""Tests for injecting custom instructions into the cover letter prompt."""

from unittest.mock import patch
from engine.domains.tailoring import render


def test_render_cover_letter_custom_instructions():
    # 1. Setup minimal inputs
    jobspec = {
        "title": "Software Engineer",
        "company": "Tech Corp"
    }
    tailoring = {
        "top_projects": [
            {
                "id": "proj1",
                "name": "Project One",
                "highlights": ["Did great things"]
            }
        ]
    }
    profile_summary = "A great developer."
    job_text = "Looking for a Software Engineer with Python experience."
    guide = "Be professional."
    custom_instructions = "Highlight my leadership experience with NATS and Kubernetes"

    # We patch stream_text to capture the 'user' prompt and prevent actual LLM call.
    with patch("engine.domains.tailoring.llm.stream_text") as mock_stream_text:
        mock_stream_text.return_value = "Mocked cover letter response"

        # Call with custom_instructions
        res = render.render_cover_letter(
            jobspec=jobspec,
            tailoring=tailoring,
            profile_summary=profile_summary,
            job_text=job_text,
            guide=guide,
            custom_instructions=custom_instructions
        )

        # Assert stream_text was called
        mock_stream_text.assert_called_once()
        
        # Get the second argument (the user prompt)
        args, kwargs = mock_stream_text.call_args
        # stream_text(system, user, max_tokens=...)
        user_prompt = args[1]
        
        # Assertions
        assert custom_instructions in user_prompt
        # And check for a clean block header as described:
        assert "## Custom Focus & Tailoring Instructions" in user_prompt


def test_cli_parser_instructions():
    from engine.cli import main
    with patch("engine.cli.cmd_new") as mock_cmd_new:
        mock_cmd_new.return_value = 0
        
        # Invoke main with custom instructions
        main(["new", "some-source-url", "--instructions", "Include a focus on distributed tracing and OpenTelemetry"])
        
        # Assert cmd_new was called with args containing instructions
        mock_cmd_new.assert_called_once()
        args = mock_cmd_new.call_args[0][0]
        assert args.source == "some-source-url"
        assert args.instructions == "Include a focus on distributed tracing and OpenTelemetry"

