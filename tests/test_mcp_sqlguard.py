import pytest
from engine.mcp.sqlguard import guard_and_wrap

def test_sqlguard_valid_queries():
    assert guard_and_wrap("SELECT * FROM jobs") == "SELECT * FROM (SELECT * FROM jobs) _q LIMIT 1000"
    assert guard_and_wrap("WITH q AS (SELECT 1) SELECT * FROM q") == "SELECT * FROM (WITH q AS (SELECT 1) SELECT * FROM q) _q LIMIT 1000"

def test_sqlguard_rejects_mutations():
    with pytest.raises(ValueError, match="only SELECT / WITH queries"):
        guard_and_wrap("INSERT INTO jobs VALUES ('nope')")
    with pytest.raises(ValueError, match="only SELECT / WITH queries"):
        guard_and_wrap("UPDATE jobs SET score = 100")
    with pytest.raises(ValueError, match="only SELECT / WITH queries"):
        guard_and_wrap("DROP TABLE jobs")

def test_sqlguard_rejects_multi_statement():
    with pytest.raises(ValueError, match="multiple statements are not allowed"):
        guard_and_wrap("SELECT * FROM jobs; DROP TABLE jobs")

def test_sqlguard_allows_semicolons_in_literals_and_comments():
    # Semicolon in string literal
    assert "hello; world" in guard_and_wrap("SELECT 'hello; world'")
    
    # Semicolon in multi-line string literal
    assert "foo; bar" in guard_and_wrap("SELECT '\\nfoo; bar\\n'")
    
    # Semicolon inside a safe SQL comment
    assert "get all jobs" in guard_and_wrap("SELECT * FROM jobs -- get all jobs;")
    
    # Semicolon inside a multi-line comment
    assert "comment" in guard_and_wrap("SELECT * FROM jobs /* multiple; statements; comment */")

def test_sqlguard_blocks_real_multistatement_after_comments():
    # Real malicious queries must still be blocked (with actual newline)
    with pytest.raises(ValueError, match="multiple statements are not allowed"):
        guard_and_wrap("SELECT * FROM jobs -- comment \n; DROP TABLE jobs")
    # Real malicious queries must still be blocked (with literal backslash-n if used as newline)
    with pytest.raises(ValueError, match="multiple statements are not allowed"):
        guard_and_wrap("SELECT * FROM jobs -- comment \\n; DROP TABLE jobs")

