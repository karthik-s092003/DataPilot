from db import app_engine
from sqlalchemy import text


def create_session(session_id):
    with app_engine.connect() as conn:
        conn.execute(text("""
            INSERT IGNORE INTO chat_sessions (session_id)
            VALUES (:session_id)
        """), {"session_id": session_id})
        conn.commit()


def save_message(session_id, role, content, sql=None):
    with app_engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO chat_messages (session_id, role, content, query)
            VALUES (:session_id, :role, :content, :query)
        """), {
            "session_id": session_id,
            "role": role,
            "content": content,
            "query": sql   # store SQL in query column
        })
        conn.commit()


def get_sessions():
    with app_engine.connect() as conn:
        result = conn.execute(text("""
            SELECT session_id, created_at
            FROM chat_sessions
            ORDER BY created_at DESC
        """))
        return [dict(row._mapping) for row in result]


def get_messages(session_id):
    with app_engine.connect() as conn:
        result = conn.execute(text("""
            SELECT role, content, query
            FROM chat_messages
            WHERE session_id = :session_id
            ORDER BY created_at
        """), {"session_id": session_id})

        
        return [
            {
                "role": row._mapping["role"],
                "content": row._mapping["content"],
                "sql": row._mapping["query"]
            }
            for row in result
        ]