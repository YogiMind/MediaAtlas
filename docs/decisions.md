# Decisions

Newest at the bottom. Don't edit old entries; add a new one that supersedes them.
Dates are approximate; adjust them to your commit history.

## SQLite, one database at the top level
**Context:** Tags and metadata need storing without altering the filesystem.
**Decision:** A single SQLite file; nothing is written into media folders.
**Alternatives:** JSON file (no real queries), TinyDB (extra dependency), per-folder files (pollutes media directories).
**Consequences:** One file to back up. Paths are absolute, so relocating a library needs a rescan.

## Layered identity: id + hash + path
**Decision:** Tags attach to a stable internal id. Hash detects duplicates and edits; path detects moves.
**Why:** No single property survives every operation (see architecture.md). Combining them lets renames keep tags.

## Namespaced tags (`namespace:value`)
**Context:** Open question whether tags should be namespaced (`genre:folk`, `context:concert`).
**Decision:** Yes. Tags are `(namespace, value)`, lowercased. A bare word becomes `tag:word`.
**Consequences:** Easy filtering by category; automatic tags use their own namespace (`folder`) so they can be regenerated without touching manual ones.

## Python + FastAPI (supersedes "Flask or FastAPI?")
**Decision:** FastAPI.
**Why:** Auto-generated `/docs` for testing without a frontend, validation from type hints, JSON-first. Raw framework speed doesn't matter; hashing and disk are the bottlenecks.
**Consequences:** Performance work later targets the core (faster hashing, native code for hot spots) behind the same function signatures.

## Thin API/CLI over a core with no I/O of its own
**Decision:** Logic lives in `backend/core`; API and CLI only translate.
**Why:** Keeps each layer replaceable and testable; the same functions serve both front doors.

## Non-destructive scanning, dry-run by default
**Decision:** `scan` reports changes and writes nothing without `--apply`; missing files are kept unless `--delete-removed`.
**Why:** A bug or an unplugged drive shouldn't destroy tagging work.

## Frontend: HTML/CSS + a small JS library, no build step (proposed)
**Decision:** Plain HTML with Alpine.js, served by FastAPI. Not final until the first page exists.
**Why:** Fastest route to something usable while still learning fetch, events, and the DOM. Because the frontend only uses the JSON API, it can be rewritten in React/Vue later.
**Rejected:** Next.js (duplicates the backend), React from the start (build tooling before a first page).

## Metadata: columns for core facts, JSON for the rest (proposed)
**Decision:** Identity and filtering fields (path, type, hash, size, modified time) are real columns. Media-specific details (duration, resolution, artist, ...) go in the `assets.metadata` JSON column.
**Why:** Core fields are queried constantly and benefit from indexes; media fields vary by type and change often.
**Open:** Promote a metadata field to its own column when you start filtering or sorting by it.

## Files: What does same file mean?
**Context** What is concidered to be the same file? Currently both rename and modification registers as deletion + new file, removing the tags. And what about a trimmed recording?
**Decision:** Tiered pipeline, cheapest first: 1. Metadata and filesystem identity (size, mtime, inode); 2. Exact content hashing; 3. Perceptual fingerprints for media (same media, different bytes)
