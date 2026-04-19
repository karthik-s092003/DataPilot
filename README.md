🚀 QueryAI — AI-Powered Database Chatbot

QueryAI is an intelligent chatbot that allows users to interact with a database using natural language.
Instead of writing SQL queries manually, users can simply ask questions, and QueryAI generates SQL, executes it, 
and returns results in a human-readable format.

✨ Features
🧠 Natural Language → SQL conversion
🔍 Dynamic schema fetching (no hardcoded schema)
💬 Conversational memory (follow-up questions supported)
⚡ FastAPI backend with async processing
🎨 ChatGPT-like UI built with React
⏳ Typing animation & loading indicators
🔐 Safe query execution (SELECT-only protection)

🏗️ Tech Stack
Backend
Python
FastAPI
SQLAlchemy
AutoGen (LLM agents)
MySQL
Frontend
React.js
CSS (custom styling)
Fetch API

Project Structure:
ChatBot/
├── backend/
│   ├── db.py
│   ├── schema.py
│   ├── ai.py
│   ├── main.py
│   └── .env
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── App.jsx
│   │   └── main.jsx
│   └── .env
│
└── README.md

🔐 Security
Only SELECT queries are allowed
Prevents destructive SQL operations
Input validation and query filtering

Acknowledgements
OpenAI / Groq for LLM APIs
FastAPI for backend framework
React for frontend


