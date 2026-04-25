from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text, create_engine
from sqlalchemy.exc import SQLAlchemyError

from schema import fetch_schema
from ai import generate_sql, generate_answer
from db import app_engine

from memory import (
    create_session,
    save_message,
    get_sessions,
    get_messages,
    save_db_connection,
    get_db_connection
)

from auth import create_token
from auth_dependency import get_current_user

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# MODELS
# =========================
class QueryRequest(BaseModel):
    question: str
    session_id: str


class AuthRequest(BaseModel):
    email: str
    password: str


class DBConfig(BaseModel):
    host: str = "localhost"
    username: str
    password: str
    database: str


# =========================
# UTILS
# =========================
def is_safe_query(sql: str):
    sql = sql.lower().strip()
    return sql.startswith("select")


# =========================
# AUTH APIs
# =========================
@app.post("/register")
def register(req: AuthRequest):
    with app_engine.connect() as conn:

        existing = conn.execute(text("""
            SELECT id FROM users WHERE email = :email
        """), {"email": req.email}).fetchone()

        if existing:
            raise HTTPException(status_code=400, detail="User already exists")

        conn.execute(text("""
            INSERT INTO users (email, password)
            VALUES (:email, :password)
        """), {
            "email": req.email,
            "password": req.password
        })

        conn.commit()

    return {"message": "User registered"}


@app.post("/login")
def login(req: AuthRequest):
    with app_engine.connect() as conn:

        user = conn.execute(text("""
            SELECT id, password FROM users WHERE email = :email
        """), {"email": req.email}).fetchone()

        if not user or user._mapping["password"] != req.password:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token = create_token(user._mapping["id"])

        return {"token": token}


# =========================
# DB CONNECTION APIs
# =========================
@app.post("/test-db")
def test_db(config: DBConfig, user_id: int = Depends(get_current_user)):
    try:
        url = f"mysql+pymysql://{config.username}:{config.password}@{config.host}/{config.database}"
        engine = create_engine(url)

        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        return {"success": True}

    except SQLAlchemyError as e:
        return {"success": False, "error": str(e)}


@app.post("/connect-db")
def connect_db(config: DBConfig, user_id: int = Depends(get_current_user)):
    try:
        url = f"mysql+pymysql://{config.username}:{config.password}@{config.host}/{config.database}"
        engine = create_engine(url)

        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        # ✅ SAVE IN DB
        save_db_connection(user_id, config)

        return {"success": True}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/has-db")
def has_db(user_id: int = Depends(get_current_user)):
    db = get_db_connection(user_id)
    return {"connected": bool(db)}


# =========================
# CHAT API
# =========================
@app.post("/chat")
async def chat(req: QueryRequest, user_id: int = Depends(get_current_user)):
    try:
        session_id = req.session_id

        # 🔥 GET USER DB CONFIG
        db_config = get_db_connection(user_id)

        if not db_config:
            raise HTTPException(status_code=400, detail="Database not connected")

        db_url = f"mysql+pymysql://{db_config['username']}:{db_config['password']}@{db_config['host']}/{db_config['database']}"
        user_engine = create_engine(db_url)

        # Session
        create_session(session_id, user_id)

        history = get_messages(session_id, user_id)[-6:]

        schema = fetch_schema()

        sql_query = await generate_sql(req.question, schema, history)

        if not is_safe_query(sql_query):
            raise HTTPException(status_code=400, detail=f"Unsafe query: {sql_query}")

        # Execute
        with user_engine.connect() as conn:
            result = conn.execute(text(sql_query))
            rows = result.fetchall()

        data = [dict(row._mapping) for row in rows]

        answer = await generate_answer(req.question, data, history)

        save_message(session_id, user_id, "user", req.question)
        save_message(session_id, user_id, "assistant", answer, sql_query)

        return {
            "sql": sql_query,
            "data": data,
            "answer": answer
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# SESSIONS
# =========================
@app.get("/sessions")
def sessions(user_id: int = Depends(get_current_user)):
    return get_sessions(user_id)


@app.get("/sessions/{session_id}")
def session_messages(session_id: str, user_id: int = Depends(get_current_user)):
    return get_messages(session_id, user_id)