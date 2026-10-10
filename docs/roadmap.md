# Roadmap

_Updated: 2026-10-10._

**Now:** first frontend page; tests for the API layer; documentation rewrite.

## Phases

1. **Core database functionality**: done
2. **Minimal API (FastAPI)**: done; every backend action is reachable and testable via `/docs`
3. **Very simple frontend**: *current*; list files, filter by tag, add/remove tags
4. **Richer functionality:** directory tagging, search, previews, metadata, workflow profiles, file operations
5. **Performance:** measure first, then optimized libraries, then native code only where profiling points

## Next (high priority)

- [ ] Minimal frontend: `frontend/index.html` served by FastAPI
- [ ] API tests: one per endpoint (TestClient + temp database)
- [ ] Tests for folder tagging (`propose_folder_tags`, `apply_tag_proposal`)
- [ ] Tests for modified and removed paths through `apply_changes`
- [ ] Skip hashing when size and mtime are unchanged

## Soon (medium priority)

- [ ] `status` column ("present" / "missing") so unplugged drives don't lose tags
- [ ] Untag in CLI and frontend (`remove_asset_tag` exists; only the API uses it)
- [ ] Design directory tagging (separate table, or directories as assets?)
- [ ] Search by file name and media type, not only tags
- [ ] Skip and report unreadable files instead of crashing the scan
- [ ] Ignore rules: hidden files and folders, `.DS_Store`, temp files
- [ ] Config file or environment variables for DB path and library roots
- [ ] File preview in the UI via `/api/assets/{id}/file`
- [ ] Decide relative vs absolute paths (a library root per drive)
- [ ] Case-insensitive tags in the schema (currently lowercased in `parse_tag`)

## Later (low priority)

- [ ] Rename, move, create, and delete files from the app (needs a safety design: trash folder, confirmation)
- [ ] Background scans with progress reporting
- [ ] Faster hash (blake2b / blake3 / xxhash), then parallel hashing
- [ ] SQLite tuning (WAL mode, batched inserts)
- [ ] File watcher (`watchdog`)
- [ ] Metadata extraction (`mutagen`, Pillow/EXIF), thumbnails, waveforms
- [ ] Workflow profiles
- [ ] Schema migrations (`PRAGMA user_version`) once the DB holds real data
- [ ] Authentication, if the server is ever exposed beyond localhost
- [ ] Profile with cProfile; only then consider C/Rust

## Done

- Database schema, data access layer (`db.py`)
- Chunked file hashing
- Change detection (`check_state`: new / modified / renamed / removed, including duplicate files)
- Applying changes (`apply_changes`); renames keep asset id and tags
- Folder-based tag proposals (tests still missing)
- Tag queries: files with ALL given tags
- Scans restricted to the scanned folder
- Command-line interface (scan, list, tag, find, tags)
- FastAPI layer (assets, tags, scan, file streaming)
- Test setup with pytest and temp folders; rename-keeps-tags verified
- Docstrings and schema comments; README
