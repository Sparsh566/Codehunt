import os
import shutil
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.app.config import settings

db_url = settings.DATABASE_URL
if os.environ.get("VERCEL") and "sqlite" in db_url:
    tmp_db = Path("/tmp/codehunt.db")
    if not tmp_db.exists():
        repo_db = Path(__file__).resolve().parent.parent.parent.parent / "codehunt.db"
        if not repo_db.exists():
            repo_db = Path(__file__).resolve().parent.parent.parent / "codehunt.db"
        if repo_db.exists():
            try:
                shutil.copyfile(str(repo_db), str(tmp_db))
            except Exception:
                pass
    db_url = "sqlite:////tmp/codehunt.db"

connect_args = {}
if db_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    db_url,
    connect_args=connect_args,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
