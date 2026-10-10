# Architecture

_Status: describes the implemented system. Last reviewed: 2026-10-10._

## Purpose

Manage and structure media files (audio, photos, video) by meaning instead of
folder position. Files get tags, and the app tracks each file's *identity* so
that renaming or moving it never loses its tags.

## Layers

```
frontend (planned) ─HTTP/JSON─▶ backend/api  ─▶ backend/core ─▶ SQLite
command line (main.py) ─────────────────────▶ backend/core
```

Rules:

1. `core` contains all logic. It never imports from `api` or the CLI, and never prints.
2. The API and CLI are thin: parse input, call `core`, format output.
3. The frontend knows only the JSON API, so it can be replaced without touching the backend.
4. MediaAtlas is **non-destructive**: it reads files but never moves, renames, or deletes them.

## Modules

| Module | Responsibility |
|---|---|
| `core/db.py` | All SQL. The only module that talks to SQLite. |
| `core/scanner.py` | `check_state` (detect changes), `apply_changes` (update the DB) |
| `core/tagging.py` | Folder-based tag proposals (`propose_folder_tags`, `apply_tag_proposal`) |
| `core/utils.py` | File hashing, media type guessing, tag parsing |
| `core/schema.sql` | Database schema |
| `api/app.py` | FastAPI routes |
| `main.py` | Command-line interface |

## File identity (layered)

"Is this the same file?" has no single answer, so MediaAtlas combines three:

| Layer | Implemented as | Purpose |
|---|---|---|
| **Primary ID** | `assets.id` (SQLite) | Never changes. Tags attach to this. |
| **Content identity** | `assets.content_hash` (SHA-256) | Detect duplicates and content changes |
| **Location** | `assets.path` | Where the file is now; used to detect renames and moves |

Alternatives considered and not used:

- **Name:** changes on rename.
- **Inode / file ID:** OS-specific, and not reliable across drives or copies. Hash plus path covers the same cases portably.
- **Size + modified time:** not used as identity, but *planned* as a cheap check to skip re-hashing unchanged files.

## Data model

SQLite, see `core/schema.sql`.

- `assets`: one row per file: path (unique), media type, content hash, size, modified time, metadata (JSON text)
- `tags`: unique `(namespace, value)` pairs, e.g. `genre:folk`
- `asset_tags`: many-to-many link between assets and tags; deleting an asset or tag removes its links

## Change detection

`check_state(conn, root)` compares disk against the database for one scanned
folder and classifies every difference:

1. **Pass 1, match by path.** Path in both: same hash is unchanged, different hash is **modified**. Path only on disk: held back as a candidate.
2. **Pass 2, match leftovers by hash.** A database path missing from disk whose hash matches a held-back file is a **rename/move**. No match means **removed**.
3. **Pass 3.** Whatever is still held back is **new** (including extra copies).

`apply_changes` then updates the database. A rename is a path update on the same
row, so the asset keeps its id and tags. Removed files stay in the database
unless `delete_removed=True`, so an unplugged drive doesn't wipe your tags.

### Known limitations

- A file edited **and** renamed between scans looks like removed + new (it loses its tags).
- Empty files all share one hash and can be mistaken for renames.
- Every scan re-hashes every file.
- Paths are absolute; moving a whole library needs a rescan.

## Folder-based tags

`propose_folder_tags(root)` builds a proposal (tag name → file paths) from the
folders each file sits in, without touching the database. `apply_tag_proposal`
writes it, optionally with renamed tags, under the `folder` namespace. The
split exists so the user can review and edit names before anything is applied.
