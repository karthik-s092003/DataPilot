from db import app_engine
from sqlalchemy import text


# =========================
# CREATE SESSION
# =========================
def create_session(session_id, user_id):
    with app_engine.connect() as conn:
        conn.execute(text("""
            INSERT IGNORE INTO chat_sessions (session_id, user_id)
            VALUES (:session_id, :user_id)
        """), {
            "session_id": session_id,
            "user_id": user_id
        })
        conn.commit()


# =========================
# SAVE MESSAGE
# =========================
def save_message(session_id, user_id, role, content, sql=None):
    with app_engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO chat_messages (session_id, user_id, role, content, query)
            VALUES (:session_id, :user_id, :role, :content, :query)
        """), {
            "session_id": session_id,
            "user_id": user_id,
            "role": role,
            "content": content,
            "query": sql
        })
        conn.commit()


# =========================
# GET SESSIONS (USER BASED)
# =========================
def get_sessions(user_id):
    with app_engine.connect() as conn:
        result = conn.execute(text("""
            SELECT session_id, created_at
            FROM chat_sessions
            WHERE user_id = :user_id
            ORDER BY created_at DESC
        """), {"user_id": user_id})

        return [dict(row._mapping) for row in result]


# =========================
# GET MESSAGES (USER BASED)
# =========================
def get_messages(session_id, user_id):
    with app_engine.connect() as conn:
        result = conn.execute(text("""
            SELECT role, content, query
            FROM chat_messages
            WHERE session_id = :session_id
            AND user_id = :user_id
            ORDER BY created_at
        """), {
            "session_id": session_id,
            "user_id": user_id
        })

        return [
            {
                "role": row._mapping["role"],
                "content": row._mapping["content"],
                "sql": row._mapping["query"]
            }
            for row in result
        ]