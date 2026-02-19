import sqlite3
from pathlib import Path
from backend.core.scanner import import_files, find_changes, check_state

# DIR = Path("/home/scazarch/Pictures")
PROJ_DIR = Path("/home/scazarch/Dev/Projects/MediaAtlas")
DIR = PROJ_DIR / "assets/sample_files"
DB = PROJ_DIR / "data/sample.db"
SQL = PROJ_DIR / "backend/core/schema.sql"

if __name__ == "__main__":
    with sqlite3.connect(DB) as conn:

        # Create tables
        with open(SQL) as f:
            conn.executescript(f.read())

        # import_files(conn, DIR)
        #
        # # generate_tags(conn, DIR)
        # find_changes(conn, DIR)
        check_state(conn, DIR)

