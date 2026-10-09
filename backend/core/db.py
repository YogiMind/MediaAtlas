import json
import sqlite3

def connect(db_path):
    """Open the MediaAtlas database with foreign keys on and name-based row access."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row   # row["path"] instead of row[1]
    return conn


def update_path(conn, old_path, new_path):
    """Point an existing asset at a new path. Its id, and so its tags, are kept."""
    conn.execute("UPDATE assets SET path=? WHERE path=?", (new_path, old_path))


def update_file_info(conn, path, content_hash, size, modified):
    """Refresh hash, size and mtime of an asset after its contents changed."""
    conn.execute(
        "UPDATE assets SET content_hash=?, size=?, modified=? WHERE path=?",
        (content_hash, size, modified, path),
    )


# ---------- Assets ----------

def add_asset(conn, path, media_type, content_hash, size, modified, metadata: dict):
    """Insert one file into the assets table.

    Args:
        conn: Open sqlite3 connection (caller is responsible for committing).
        path: Full path of the file on disk.
        media_type: e.g. "audio", "image", "video".
        content_hash: Hash of the file's contents (its identity).
        size: File size in bytes.
        modified: Last-modified timestamp from the filesystem.
        metadata: Extra info as a dict; stored as a JSON string.
    """
    sql = """
    INSERT INTO assets (path, media_type, content_hash, size, modified, metadata)
    VALUES (?, ?, ?, ?, ?, ?)
    """
    conn.execute(sql, (path, media_type, content_hash, size, modified, json.dumps(metadata)))


def remove_asset(conn, path):
    """Delete an asset. Its asset_tags rows go too (ON DELETE CASCADE)."""
    conn.execute("DELETE FROM assets WHERE path=?", (path,))


def hash_exists(conn, content_hash):
    """Return True if any asset with this content hash is in the database."""
    row = conn.execute(
        "SELECT 1 FROM assets WHERE content_hash = ? LIMIT 1",
        (content_hash,)
    ).fetchone()
    return row is not None   # fetchone() gives None when nothing matched


def get_by_hash(conn, content_hash):
    """Return all assets with this hash as (id, path, content_hash, metadata) rows.

    Returns a list, because identical files at different paths share a hash.
    """
    rows = conn.execute(
        "SELECT id, path, content_hash, metadata FROM assets WHERE content_hash=?",
        (content_hash,)
    ).fetchall()
    return rows


def path_exists(conn, path):
    """Return True if an asset with this exact path is in the database."""
    row = conn.execute(
        "SELECT 1 FROM assets WHERE path = ? LIMIT 1",
        (path,)
    ).fetchone()
    return row is not None


def get_by_path(conn, path):
    """Return the asset(s) at this path as (id, path, content_hash, metadata) rows.

    Returns a list (empty if not found).
    """
    row = conn.execute(
        "SELECT id, path, content_hash, metadata FROM assets WHERE path=?",
        (path,)
    ).fetchall()
    return row


# ---------- Tags ----------

def add_tag(conn, namespace, value):
    """Create a tag like ("mood", "dark"); does nothing if it already exists.

    Relies on a UNIQUE(namespace, value) constraint in the schema.
    """
    conn.execute(
        "INSERT OR IGNORE INTO tags (namespace, value) VALUES (?, ?)",
        (namespace, value)
    )


def add_asset_tag(conn, asset_id, tag_id):
    """Attach a tag to an asset; does nothing if already attached.

    Relies on a PRIMARY KEY / UNIQUE on (asset_id, tag_id) in the schema.
    """
    conn.execute(
        "INSERT OR IGNORE INTO asset_tags (asset_id, tag_id) VALUES (?, ?)",
        (asset_id, tag_id)
    )


def get_or_create_tag(conn, namespace, value):
    """Return the id of this tag, creating it first if needed."""
    conn.execute(
        "INSERT OR IGNORE INTO tags (namespace, value) VALUES (?, ?)",
        (namespace, value)
    )
    row = conn.execute(
        "SELECT id FROM tags WHERE namespace=? AND value=?",
        (namespace, value)
    ).fetchone()
    return row[0]
