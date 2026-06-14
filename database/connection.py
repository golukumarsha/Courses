import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.db_model import Base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

# ─── Tables auto-create ───────────────────────────────
Base.metadata.create_all(bind=engine)

# ─── Session ──────────────────────────────────────────
Session = sessionmaker(bind=engine)


# ─── Dependency ───────────────────────────────────────
def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()
