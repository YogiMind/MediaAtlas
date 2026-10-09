from pathlib import Path
from backend.core.db import connect
from backend.core.scanner import check_state, apply_changes
from backend.core.tagging import propose_folder_tags, apply_tag_proposal


PROJ_DIR = Path(__file__).parent          # no more hardcoded home directory
DIR = PROJ_DIR / "assets/sample_files"
DB = PROJ_DIR / "data/sample.db"
SQL = PROJ_DIR / "backend/core/schema.sql"

if __name__ == "__main__":
    with connect(DB) as conn:             # commits on success, rolls back on error
        conn.executescript(SQL.read_text())

        changes = check_state(conn, DIR)
        print(changes)
        apply_changes(conn, changes)

        proposal = propose_folder_tags(DIR)
        apply_tag_proposal(conn, proposal)

