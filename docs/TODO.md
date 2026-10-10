# Phases

**1. Basic db functionality** ✅
- Query the database
- Add files
- Add tags

**2. Minimal API** (FastAPI) ✅
An API call for every action in the backend; backend only responds to requests.
Tested interactively through /docs.

**3. Very simple frontend** ← current phase
- Single HTML page that talks to the backend via the API
- Display files in the database, filter by tag, add/remove tags

**4. Increase functionality complexity**
Now with a basic, testable architecture, add more core functionality:
- Directory tagging and dashboard
- Move, rename and create files on disk (keeps identity and tags)
- Metadata, thumbnails, workflow profiles

**5. Performance and scale**
Measure first, then optimized libraries, then native code (C/Rust) only if needed.


# Tasks

### High priority
- [ ] Minimal frontend: `frontend/index.html` served by FastAPI (list files, tag filter, add tag)
- [ ] API tests: one per endpoint, using TestClient and a temp database
- [ ] README: add a Status section and "How to run" (CLI and server)
- [ ] Tests for folder tagging (`propose_folder_tags`, `apply_tag_proposal`)
- [ ] Tests for modified and removed paths through `apply_changes`
- [ ] Skip hashing for files whose size and mtime are unchanged (core scan speedup)

### Medium priority
- [ ] `status` column on assets ("present" / "missing"), so unplugged drives don't lose tags
- [ ] Untag in CLI and frontend (`remove_asset_tag` exists, only exposed in the API)
- [ ] Design directory tagging (separate table, or directories as assets?)
- [ ] Search by file name and media type, not only by tag
- [ ] Error handling in scanning: unreadable files are skipped and reported, not fatal
- [ ] Ignore rules: hidden files and folders, `.DS_Store`, temp files
- [ ] Config file or environment variables for DB path and library roots
- [ ] Preview in the UI: stream files via `/api/assets/{id}/file` (audio player, image view)
- [ ] Case-insensitive tags handled in the schema (currently lowercased in `parse_tag`)
- [ ] Decide on relative vs absolute paths (a library root per drive)

### Low priority
- [ ] Rename and move files from the app (updates the DB path, keeps id and tags)
- [ ] Delete files from the app (needs a safety design: trash folder, confirmation)
- [ ] Background scans with progress reporting (needed once scans take minutes)
- [ ] Faster hash (blake2b / blake3 / xxhash), then parallel hashing
- [ ] SQLite tuning (WAL mode, batched inserts)
- [ ] File watcher for automatic rescans (`watchdog`)
- [ ] Metadata extraction (`mutagen` for audio, Pillow/EXIF for photos)
- [ ] Thumbnails and waveforms
- [ ] Workflow profiles (default tags, file-type rules per workflow)
- [ ] Schema migrations (`PRAGMA user_version`) once the DB holds real data
- [ ] Authentication, if the server is ever exposed beyond localhost
- [ ] Profile with cProfile; only then consider C/Rust for hot spots


# In Progress
- Frontend: first HTML page
- Tests for the API layer


# Done
- Database schema (assets, tags, asset_tags, foreign keys, indexes)
- Data access layer (`db.py`)
- Import files to database
- Avoid duplicates (based on Path and Hash)
- Chunked file hashing (`hash_file`)
- State change detection (`check_state`: new / modified / renamed / removed, incl. duplicate files)
- Apply detected changes to the DB (`apply_changes`); renames keep asset id and tags
- Generate tags based on dir-structure (`propose_folder_tags`, `apply_tag_proposal`), still needs tests
- Tag queries: find files with ALL given tags
- Scans limited to the scanned folder
- Command-line interface (scan, list, tag, find, tags)
- FastAPI layer (assets, tags, scan, file streaming) with auto-generated /docs
- Test setup with pytest and temp folders; rename-keeps-tags verified
- Code documentation: docstrings and schema comments
