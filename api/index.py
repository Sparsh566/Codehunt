import sys
import os
import shutil
from pathlib import Path

# Add project root directory to sys.path so 'backend' package is importable
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

# Ensure Vercel serverless environment has a writable database directory
if os.environ.get("VERCEL"):
    tmp_db = Path("/tmp/codehunt.db")
    if not tmp_db.exists():
        repo_db = root_dir / "backend" / "codehunt.db"
        if not repo_db.exists():
            repo_db = root_dir / "codehunt.db"
        if repo_db.exists():
            try:
                shutil.copyfile(str(repo_db), str(tmp_db))
            except Exception:
                pass

from backend.app.main import app
