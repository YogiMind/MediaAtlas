PRAGMA foreign_keys = ON;


CREATE TABLE IF NOT EXISTS assets (
    id INTEGER PRIMARY KEY,
    path TEXT NOT NULL,
    media_type TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    size INTEGER NOT NULL,
    modified REAL NOT NULL,
    metadata TEXT,
    UNIQUE(path)
);

CREATE INDEX IF NOT EXISTS idx_assets_path ON assets(path);
CREATE INDEX IF NOT EXISTS idx_assets_hash ON assets(content_hash);


CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY,
    namespace TEXT NOT NULL,
    value TEXT NOT NULL,
    UNIQUE(namespace, value)
);

CREATE TABLE IF NOT EXISTS asset_tags (
    asset_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (asset_id, tag_id),
    FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);
