-- Enforce foreign keys. NOTE: this is per-connection; see connect() helper.
PRAGMA foreign_keys = ON;


-- ASSETS: one row per media file. The row's `id` is the file's stable internal
-- identity: path and content can change, the id (and its tags) stay.
CREATE TABLE IF NOT EXISTS assets (
    id INTEGER PRIMARY KEY,          -- internal ID (auto-assigned)
    path TEXT NOT NULL,              -- current location on disk (absolute)
    media_type TEXT NOT NULL,        -- "audio", "image", "video", ...
    content_hash TEXT NOT NULL,      -- hash of file contents (NOT unique: copies share it)
    size INTEGER NOT NULL,           -- bytes
    modified REAL NOT NULL,          -- filesystem mtime (Unix timestamp, float)
    metadata TEXT,                   -- extra info as a JSON string
    UNIQUE(path)                     -- two rows can't claim the same path
);

-- Fast lookup by hash (rename/duplicate detection). The UNIQUE(path)
-- constraint above already creates an index for path lookups.
CREATE INDEX IF NOT EXISTS idx_assets_hash ON assets(content_hash);


-- TAGS: a vocabulary of tags, e.g. ("mood", "dark"), ("instrument", "guitar").
CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY,
    namespace TEXT NOT NULL,         -- category of the tag
    value TEXT NOT NULL,             -- the tag itself
    UNIQUE(namespace, value)         -- each tag exists only once
);


-- ASSET_TAGS: join table for the many-to-many link between assets and tags.
-- One row = "this asset has this tag".
CREATE TABLE IF NOT EXISTS asset_tags (
    asset_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (asset_id, tag_id),  -- an asset can't have the same tag twice
    FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE CASCADE,  -- delete asset -> its links go too
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE       -- delete tag -> its links go too
);
