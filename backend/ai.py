import os
import asyncio
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import ModelFamily
from autogen_agentchat.agents import AssistantAgent
from pydantic import BaseModel
import json

class SQLResponse(BaseModel):
    sql: str


from dotenv import load_dotenv

load_dotenv()



async def generate_sql(question, schema, history):

    groq_model_client = OpenAIChatCompletionClient(
        model=os.getenv("OPENAI_MODEL_NAME", "openai/gpt-oss-120b"),
        base_url=os.getenv("OPENAI_API_BASE", "https://api.groq.com/openai/v1"),
        api_key=os.getenv("GROQ_API_KEY"),
        response_format=SQLResponse,
        model_info={
            "vision": False,
            "function_calling": True,
            "json_output": True,
            "family": ModelFamily.UNKNOWN,
            "structured_output": True,
        },
    )
    
    assistant = AssistantAgent(
        name="sql_generator",
        system_message=f"""
        You are an SQL generator.

        for your context, here are some previous questions and SQL queries that you generated:
        {history}, use it as reference to generate the SQL for the current question.

        Rules:
        - Only generate sql queries for the asked quetion {question}
        - No explanations
        - Use this schema:

        {schema}
        """,
        model_client=groq_model_client
    )

    result = await assistant.run(task="generate an SQL query to answer the question based on the given database schema")

    content = result.messages[-1].content
    print(content)

    await groq_model_client.close()

    try:
        parsed = json.loads(content)
        return parsed.get("sql", content)
    except:
        return content



async def generate_answer(question, result, history):
    groq_model_client = OpenAIChatCompletionClient(
        model=os.getenv("OPENAI_MODEL_NAME", "openai/gpt-oss-120b"),
        base_url=os.getenv("OPENAI_API_BASE", "https://api.groq.com/openai/v1"),
        api_key=os.getenv("GROQ_API_KEY"),
        model_info={
            "vision": False,
            "function_calling": True,
            "json_output": True,
            "family": ModelFamily.UNKNOWN,
            "structured_output": False,
        },
    )

    assistant = AssistantAgent(
        name="answer_generator",
        system_message=f"""
        You are an answer generator who converts the given result {result} into a natural language answer.

        for your context, here are some previous questions and answers, use it as reference to answer the current question:
        {history}

        Rules:
        - This was the asked question: {question}
        - No explanations
        """,
        model_client=groq_model_client
    )

    result = await assistant.run(task="generate an answer to the question based on the sql query result")
    print(result.messages[-1].content)

    await groq_model_client.close()
    return result.messages[-1].content

if __name__ == "__main__":

    schema = """
    Table: employees
    - id (INT, PRIMARY KEY)
    - name (VARCHAR)
    - age (INT)
    - department_id (INT)
    - salary (INT)

    Table: departments
    - id (INT, PRIMARY KEY)
    - department_name (VARCHAR)

    Table: projects
    - id (INT, PRIMARY KEY)
    - project_name (VARCHAR)
    - department_id (INT)

    Table: employee_projects
    - employee_id (INT)
    - project_id (INT)
    """
    question1 = "Get names of all employees"
    result = ['John Doe', 'Jane Smith', 'Alice Johnson']

    asyncio.run(generate_sql(question1, schema))