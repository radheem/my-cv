import json
import pytest
import psycopg
from engine.db import get_conn, init_db
from engine.mcp.server import cv_tailor_ontology, query


def test_mcp_ontology():
    ont = json.loads(cv_tailor_ontology())
    assert "tables" in ont
    assert "jobs" in ont["tables"]
    assert "applications" in ont["tables"]


def test_mcp_query():
    try:
        with get_conn():
            pass
    except psycopg.OperationalError:
        pytest.skip("PostgreSQL offline. Skipping MCP server queries integration test.")

    init_db()
    
    # 1. Test basic COUNT (integer output)
    res = json.loads(query("SELECT COUNT(*) FROM jobs"))
    assert "rows" in res
    assert len(res["rows"]) >= 1
    assert "count" in res["rows"][0]

    # 2. Test aggregation queries (resulting in Decimal / numeric values)
    res_avg = json.loads(query("SELECT AVG(COALESCE(score, 0))::numeric as avg_score FROM jobs"))
    assert "rows" in res_avg
    assert "avg_score" in res_avg["rows"][0]
    # Check that decimal translates successfully into float or is serializable
    assert isinstance(res_avg["rows"][0]["avg_score"], (int, float))

    # 3. Test datetime representation serialization (should match ISO-8601)
    res_dates = json.loads(query("SELECT NOW() as current_time"))
    assert "rows" in res_dates
    assert "current_time" in res_dates["rows"][0]
    assert isinstance(res_dates["rows"][0]["current_time"], str)

    # 4. Test execution isolation & error packaging on syntax failure
    res_err = json.loads(query("SELECT invalid_column_name_xyz FROM jobs"))
    assert "error" in res_err
    assert "does not exist" in res_err["error"]
