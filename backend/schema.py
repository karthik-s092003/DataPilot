from db import engine
from sqlalchemy import text

def fetch_schema():
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = 'company_db'
            ORDER BY TABLE_NAME, ORDINAL_POSITION;
        """))

        rows = result.fetchall()

    schema_map = {}

    for row in rows:
        table = row[0]
        column = f"{row[1]} ({row[2]})"

        if table not in schema_map:
            schema_map[table] = []
        schema_map[table].append(column)

    schema_str = ""
    for table, cols in schema_map.items():
        schema_str += f"Table: {table}\n"
        for c in cols:
            schema_str += f"- {c}\n"
        schema_str += "\n"

    return schema_str