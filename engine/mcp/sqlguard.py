import re

_SELECT_RE = re.compile(r"(?is)^\s*(with|select)\b")
ROW_CAP = 1000

def _strip_comments_and_literals(sql: str) -> str:
    """Strip string literals and SQL comments to safely inspect for query separators."""
    out = []
    i = 0
    n = len(sql)
    while i < n:
        # 1. Multi-line comments: /* ... */
        if sql[i:i+2] == "/*":
            i += 2
            while i < n and sql[i:i+2] != "*/":
                i += 1
            i += 2
        # 2. Single-line comments: -- ...
        elif sql[i:i+2] == "--":
            i += 2
            while i < n:
                if sql[i] == "\n":
                    break
                if sql[i:i+2] == "\\n":
                    i += 2
                    break
                i += 1
        # 3. Single-quoted literals: '...'
        elif sql[i] == "'":
            i += 1
            while i < n:
                if sql[i] == "'":
                    if i + 1 < n and sql[i+1] == "'": # Doubled single quote escape
                        i += 2
                        continue
                    i += 1
                    break
                elif sql[i] == "\\": # Backslash escape (standard in some SQL modes)
                    i += 2
                else:
                    i += 1
        # 4. Double-quoted literals/identifiers: "..."
        elif sql[i] == '"':
            i += 1
            while i < n:
                if sql[i] == '"':
                    if i + 1 < n and sql[i+1] == '"': # Doubled double quote escape
                        i += 2
                        continue
                    i += 1
                    break
                elif sql[i] == "\\":
                    i += 2
                else:
                    i += 1
        else:
            out.append(sql[i])
            i += 1
    return "".join(out)

def guard_and_wrap(sql: str, row_cap: int = ROW_CAP) -> str:
    """Validate query and wrap it read-only + row-capped."""
    s = sql.strip().rstrip(";").strip()
    if not _SELECT_RE.match(s):
        raise ValueError("only SELECT / WITH queries are allowed")
    
    # Strip comments and literals before checking for semicolons
    cleaned_sql = _strip_comments_and_literals(s)
    if ";" in cleaned_sql:
        raise ValueError("multiple statements are not allowed")
        
    return f"SELECT * FROM ({s}) _q LIMIT {row_cap}"

