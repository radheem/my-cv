from __future__ import annotations

import os
import pytest
import psycopg
from engine.db import get_conn, init_db

def test_db_initialization():
    try:
        with get_conn():
            pass
    except psycopg.OperationalError:
        pytest.skip("PostgreSQL container is offline. Skipping database integration tests.")

    # Setup test schema
    init_db()
    
    with get_conn() as conn:
        with conn.cursor() as cur:
            # Check tables exist
            cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
            tables = [row["table_name"] for row in cur.fetchall()]
            assert "jobs" in tables
            assert "applications" in tables

