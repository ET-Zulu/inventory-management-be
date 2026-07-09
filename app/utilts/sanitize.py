"""
Search input sanitization – prevents LIKE-wildcard injection.

WHY THIS EXISTS
---------------
SQLAlchemy's ORM already prevents classic SQL injection by using
parameterized queries under the hood. However there is a second,
application-level risk: if a user types a bare '%' or '_' into a
search box those characters are LIKE wildcards and will match every
single row in the table, effectively dumping the whole database
through a legitimate endpoint.

This module escapes those special characters before wrapping the
value in the surrounding '%…%' pattern, and enforces a minimum
meaningful length so empty/whitespace-only inputs are skipped.

USAGE
-----
    from app.utilts.sanitize import sanitize_search_term, LIKE_ESCAPE_CHAR

    pattern = sanitize_search_term(raw_search_input)
    if pattern:
        query = query.where(
            col(Item.name).ilike(pattern, escape=LIKE_ESCAPE_CHAR)
        )

The ``escape`` keyword tells the database driver which character was
used as the escape character so it can interpret the pattern correctly.
"""

# The character we use to escape LIKE special chars. Backslash is the
# SQL standard and is supported by PostgreSQL, MySQL and SQLite.
LIKE_ESCAPE_CHAR = "\\"

# Require at least 2 non-whitespace characters – avoids extremely broad
# matches from single-character queries while still being useful.
_MIN_SEARCH_LEN = 2


def sanitize_search_term(raw: str | None) -> str | None:
    """
    Return a safe ``%…%`` LIKE pattern, or *None* if the input is too
    short or blank (so the caller can skip the WHERE clause entirely).

    Steps applied:
    1. Strip surrounding whitespace and truncate to 200 chars.
    2. Reject inputs shorter than _MIN_SEARCH_LEN.
    3. Escape the backslash itself (must come first!).
    4. Escape the LIKE wildcards ``%`` and ``_``.
    5. Wrap in ``%…%`` for a substring match.
    """
    if not raw:
        return None

    value = raw.strip()[:200]

    if len(value) < _MIN_SEARCH_LEN:
        return None

    # Order matters: escape the escape character first
    value = value.replace(LIKE_ESCAPE_CHAR, LIKE_ESCAPE_CHAR * 2)
    value = value.replace("%", LIKE_ESCAPE_CHAR + "%")
    value = value.replace("_", LIKE_ESCAPE_CHAR + "_")

    return f"%{value}%"
