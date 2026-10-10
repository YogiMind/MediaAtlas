"""MediaAtlas HTTP API: thin wrapper around backend.core."""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel

from backend.config import DB_PATH, SCHEMA_PATH
from backend.core.db import (
    connect, get_or_create_tag, add_asset_tag, remove_asset_tag,
    get_assets_by_tags, get_tags_for_asset, list_assets, list_tags,
)
from backend.core.scanner import check_state, apply_changes
from backend.core.utils import parse_tag


@asynccontextmanager
async def lifespan(app):
    """Runs once at startup: make sure the database and tables exist."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with connect(DB_PATH) as conn:
        conn.executescript(SCHEMA_PATH.read_text())
    yield


app = FastAPI(title="MediaAtlas", lifespan=lifespan)


def get_conn():
    """One database connection per request; commit on success, roll back on error."""
    conn = connect(DB_PATH)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def asset_to_dict(conn, row):
    """Shape a database row the way the frontend will see it."""
    return {
        "id": row["id"],
        "path": row["path"],
        "name": Path(row["path"]).name,
        "media_type": row["media_type"],
        "tags": [f"{t['namespace']}:{t['value']}" for t in get_tags_for_asset(conn, row["id"])],
    }


def parse_tags_or_422(texts):
    try:
        return [parse_tag(t) for t in texts]
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


# ---------- assets ----------

@app.get("/api/assets")
def get_assets(tag: list[str] = Query(default=[]), conn=Depends(get_conn)):
    """List assets. Repeat ?tag=mood:dark&tag=energy:high to require ALL tags."""
    tags = parse_tags_or_422(tag)
    rows = get_assets_by_tags(conn, tags) if tags else list_assets(conn)
    return [asset_to_dict(conn, r) for r in rows]


@app.get("/api/assets/{asset_id}/file")
def get_asset_file(asset_id: int, conn=Depends(get_conn)):
    """Stream the actual file. Looked up by id, so arbitrary paths can't be requested."""
    row = conn.execute("SELECT path FROM assets WHERE id=?", (asset_id,)).fetchone()
    if row is None or not Path(row["path"]).is_file():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(row["path"])


# ---------- tags ----------

class TagList(BaseModel):
    tags: list[str]          # e.g. ["mood:dark", "energy:high"]


@app.get("/api/tags")
def get_tags(conn=Depends(get_conn)):
    return [{"tag": f"{r['namespace']}:{r['value']}", "count": r["n"]} for r in list_tags(conn)]


@app.post("/api/assets/{asset_id}/tags")
def add_tags(asset_id: int, body: TagList, conn=Depends(get_conn)):
    if conn.execute("SELECT 1 FROM assets WHERE id=?", (asset_id,)).fetchone() is None:
        raise HTTPException(status_code=404, detail="No such asset")
    for namespace, value in parse_tags_or_422(body.tags):
        add_asset_tag(conn, asset_id, get_or_create_tag(conn, namespace, value))
    return {"id": asset_id, "tags": [f"{t['namespace']}:{t['value']}"
                                     for t in get_tags_for_asset(conn, asset_id)]}


@app.delete("/api/assets/{asset_id}/tags/{namespace}/{value}")
def delete_tag(asset_id: int, namespace: str, value: str, conn=Depends(get_conn)):
    remove_asset_tag(conn, asset_id, namespace.lower(), value.lower())
    return {"ok": True}


# ---------- scanning ----------

class ScanRequest(BaseModel):
    folder: str
    apply: bool = False              # dry run unless True, same as the CLI
    delete_removed: bool = False


@app.post("/api/scan")
def scan(req: ScanRequest, conn=Depends(get_conn)):
    root = Path(req.folder).resolve()
    if not root.is_dir():
        raise HTTPException(status_code=400, detail=f"Not a folder: {root}")
    changes = check_state(conn, root)
    if req.apply:
        apply_changes(conn, changes, delete_removed=req.delete_removed)
    return {"applied": req.apply, "changes": changes}
