from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "mediaatlas.db"
SCHEMA_PATH = ROOT / "backend" / "core" / "schema.sql"
