import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.db_model import Base

load_dotenv()

# ─── Engine ───────────────────────────────────────────
engine = create_engine(os.getenv("DATABASE_URL"))

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
