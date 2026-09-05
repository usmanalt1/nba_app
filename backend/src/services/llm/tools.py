RUN_SQL_QUERY_TOOL = {
    "name": "run_sql_query",
    "description": (
        "Run a single read-only SQL SELECT query against the nba_analytics views described in the "
        "system prompt and return the resulting rows. Only SELECT statements against those views are "
        "allowed - anything else is rejected before it reaches the database."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "A single read-only SQL SELECT statement."},
        },
        "required": ["query"],
        "additionalProperties": False,
    },
}