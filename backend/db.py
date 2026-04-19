from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

# =========================
# CLIENT DB (used by AI queries)
# =========================
CLIENT_DB_URL = os.getenv("DB_URL")

engine = create_engine(
    CLIENT_DB_URL,
    echo=True
)

ClientSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# =========================
# APP DB (used for chat memory)
# =========================
APP_DB_URL = os.getenv("APP_DB_URL")

app_engine = create_engine(
    APP_DB_URL,
    echo=True
)

AppSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=app_engine
)

# Base (if you use ORM later)
Base = declarative_base()


# =========================
# Dependency (Client DB)
# =========================
def get_db():
    db = ClientSessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# Dependency (App DB)
# =========================
def get_app_db():
    db = AppSessionLocal()
    try:
        yield db
    finally:
        db.close()