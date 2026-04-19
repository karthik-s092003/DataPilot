from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from schema import fetch_schema
from ai import generate_sql, generate_answer
from db import engine
from sqlalchemy import text

# ✅ NEW: DB-based memory
from memory import create_session, save_message, get_sessions, get_messages


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    question: str
    session_id: str


def is_safe_query(sql: str):
    sql = sql.lower().strip()
    return sql.startswith("select")


@app.post("/chat")
async def chat(req: QueryRequest):
    try:
        session_id = req.session_id

        # Ensure session exists
        create_session(session_id)

        # Fetch history from DB
        history = get_messages(session_id)[-6:]

        # Step 1: fetch schema
        schema = fetch_schema()

        # Step 2: generate SQL
        sql_query = await generate_sql(req.question, schema, history)

        if not is_safe_query(sql_query):
            raise HTTPException(status_code=400, detail=f"Unsafe query: {sql_query}")

        # Step 3: execute SQL (client DB)
        with engine.connect() as conn:
            result = conn.execute(text(sql_query))
            rows = result.fetchall()

        data = [dict(row._mapping) for row in rows]

        # Step 4: generate answer
        answer = await generate_answer(req.question, data, history)

        # Save to DB
        save_message(session_id, "user", req.question)
        save_message(session_id, "assistant", answer, sql_query)

        return {
            "sql": sql_query,
            "data": data,
            "answer": answer
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/sessions")
def sessions():
    return get_sessions()


@app.get("/sessions/{session_id}")
def session_messages(session_id: str):
    return get_messages(session_id)