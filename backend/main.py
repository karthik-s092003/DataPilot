from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from schema import fetch_schema
from ai import generate_sql, generate_answer
from db import engine
from sqlalchemy import text

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for dev (later restrict this)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

chat_memory = {}


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
        if session_id not in chat_memory:
            chat_memory[session_id] = []

        
        history = chat_memory[session_id]
        history = history[-6:]

        # Step 1: fetch schema
        schema = fetch_schema()

        # Step 2: generate SQL (async)
        sql_query = await generate_sql(req.question, schema, history)

        if not is_safe_query(sql_query):
            print(f"Unsafe query generated: {sql_query}")
            raise HTTPException(status_code=400, detail=f"Unsafe query generated: {sql_query}")

        # Step 3: execute SQL
        with engine.connect() as conn:
            result = conn.execute(text(sql_query))
            rows = result.fetchall()

        # Convert rows → list (for LLM readability)
        data = [dict(row._mapping) for row in rows]

        # Step 4: generate natural language answer
        answer = await generate_answer(req.question, data, history)

        # Update chat memory
        chat_memory[session_id].append({
            "role": "user",
            "content": req.question
        })

        chat_memory[session_id].append({
            "role": "assistant",
            "content": answer
        })

        return {
            "sql": sql_query,
            "data": data,
            "answer": answer
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))