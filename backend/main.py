from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from schema import fetch_schema
from ai import generate_sql, generate_answer
from db import engine, app_engine

from memory import create_session, save_message, get_sessions, get_messages
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

        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if user._mapping["password"] != req.password:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token = create_token(user._mapping["id"])

        return {"token": token}


# =========================
# CHAT API
# =========================
@app.post("/chat")
async def chat(req: QueryRequest, user_id: int = Depends(get_current_user)):
    try:
        session_id = req.session_id

        # Ensure session exists for user
        create_session(session_id, user_id)

        # Fetch history
        history = get_messages(session_id, user_id)[-6:]

        # Schema
        schema = fetch_schema()

        # Generate SQL
        sql_query = await generate_sql(req.question, schema, history)

        if not is_safe_query(sql_query):
            raise HTTPException(status_code=400, detail=f"Unsafe query: {sql_query}")

        # Execute query
        with engine.connect() as conn:
            result = conn.execute(text(sql_query))
            rows = result.fetchall()

        data = [dict(row._mapping) for row in rows]

        # Generate answer
        answer = await generate_answer(req.question, data, history)

        # Save messages
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