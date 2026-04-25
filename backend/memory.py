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

# =========================
# SAVE DB CONNECTION
# =========================
def save_db_connection(user_id, config):
    with app_engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO user_db_connections (user_id, host, username, password, database_name)
            VALUES (:user_id, :host, :username, :password, :database)
            ON DUPLICATE KEY UPDATE
                host = :host,
                username = :username,
                password = :password,
                database_name = :database
        """), {
            "user_id": user_id,
            "host": config.host,
            "username": config.username,
            "password": config.password,
            "database": config.database
        })
        conn.commit()


# =========================
# GET DB CONNECTION
# =========================
def get_db_connection(user_id):
    with app_engine.connect() as conn:
        result = conn.execute(text("""
            SELECT host, username, password, database_name
            FROM user_db_connections
            WHERE user_id = :user_id
        """), {"user_id": user_id}).fetchone()

        if not result:
            return None

        return {
            "host": result._mapping["host"],
            "username": result._mapping["username"],
            "password": result._mapping["password"],
            "database": result._mapping["database_name"]
        }