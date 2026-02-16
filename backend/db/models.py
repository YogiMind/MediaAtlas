import json

def add_asset(conn, path, media_type, content_hash, size, modified, metadata: dict):
    sql = """
    INSERT INTO assets (path, media_type, content_hash, size, modified, metadata)
    VALUES (?, ?, ?, ?, ?, ?)
    """
    conn.execute(sql, (path, media_type, content_hash, size, modified, json.dumps(metadata)))

def add_tag(conn, namespace, value):
    conn.execute(
        "INSERT OR IGNORE INTO tags (namespace, value) VALUES (?, ?)",
        (namespace, value)
    )

def add_asset_tag(conn, asset_id, tag_id):
    conn.execute(
        "INSERT OR IGNORE INTO asset_tags (asset_id, tag_id) VALUES (?, ?)",
        (asset_id, tag_id)
    )

def hash_exists(conn, content_hash):
    row = conn.execute(
        "SELECT 1 FROM assets WHERE content_hash = ? LIMIT 1",
        (content_hash,)
    ).fetchone()
    return row is not None

def get_by_hash(conn, content_hash):
    rows = conn.execute(
        "SELECT id, path, content_hash, metadata FROM assets WHERE content_hash=?",
        (content_hash,)
    ).fetchall()
    return rows

def path_exists(conn, path):
    row = conn.execute(
        "SELECT 1 FROM assets WHERE path = ? LIMIT 1",
        (path,)
    ).fetchone()
    return row is not None

def get_by_path(conn, path):
    row = conn.execute(
        "SELECT id, path, content_hash, metadata FROM assets WHERE path=?",
        (path,)
    ).fetchall()
    return row


