# MediaAtlas

A semantic layer over your filesystem for organizing media by meaning, identity, and workflow.

MediaAtlas keeps a database next to your files, without changing them. It tracks each file by what it *is*, not just where it lives, so you can rename, move, and reorganize folders without losing the tags and metadata you've built up.

> **Status: early development.** The core engine, a command-line interface, and an HTTP API work and are tested. The web interface is next. See [Roadmap](#roadmap).

## Why

Folders force every file into one place, and renaming or moving things breaks anything that referred to them. MediaAtlas adds structure on top of the filesystem:

- **Layered identity.** Every file has a content hash (what it is), a path (where it is now), and an internal ID (the stable handle tags attach to). Rename or move a file and it stays the same asset, with all its tags.
- **Structured tags.** Tags have a namespace, like `mood:dark` or `instrument:guitar`, and you can filter by any combination.
- **Non-destructive.** MediaAtlas only reads your files. Everything it knows lives in a single SQLite database, and it never moves, renames, or deletes your media.

It is aimed at audio, recordings, photos, and production workflows.

## Features

Working now:

- Scan a folder and detect what changed since the last scan: **new**, **modified**, **renamed/moved**, and **removed** files (including duplicate files)
- Apply those changes to the database; renamed files keep their ID and tags
- Dry-run by default, so nothing is written until you ask
- Tag files with `namespace:value` tags, and find files that have *all* of a set of tags
- Generate tags automatically from folder names
- Command-line interface and JSON HTTP API with interactive documentation

Planned: web interface, directory tagging, search, file previews, metadata and thumbnails, workflow profiles. See [Roadmap](#roadmap).

## Getting started

### Requirements

- Python 3.9 or newer

### Install

```bash
git clone https://github.com/YogiMind/MediaAtlas.git
cd MediaAtlas
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Command line

The database is created automatically at `data/mediaatlas.db`. Use `--db <file>` before the command to use a different one.

```bash
# See what would change in a folder (dry run, nothing is written)
python main.py scan path/to/folder

# Write the changes to the database, and tag files after their folders
python main.py scan path/to/folder --apply --folder-tags

# List everything MediaAtlas knows about
python main.py list

# Add tags to a file
python main.py tag path/to/folder/song.wav mood:dark energy:high

# Find files that have ALL of these tags
python main.py find mood:dark energy:high

# Show all tags and how many files use each
python main.py tags
```

Rename a file in your folder and scan again to see the core idea at work: it is reported as a rename (not a delete plus a new file), and after `--apply` the file keeps its tags.

Tags are written as `namespace:value`. A bare word like `dark` becomes `tag:dark`. Tags are lowercased.

Run `python main.py --help`, or `python main.py scan --help`, for all options.

### HTTP API

```bash
uvicorn backend.api.app:app --reload
```

Open **http://127.0.0.1:8000/docs** for interactive documentation where you can try every endpoint from the browser.

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/api/assets` | List files; repeat `?tag=mood:dark` to require all tags |
| `GET` | `/api/assets/{id}/file` | Stream the file itself |
| `GET` | `/api/tags` | List tags with usage counts |
| `POST` | `/api/assets/{id}/tags` | Add tags to a file |
| `DELETE` | `/api/assets/{id}/tags/{namespace}/{value}` | Remove a tag from a file |
| `POST` | `/api/scan` | Detect changes in a folder (`"apply": true` to write them) |

The server listens on localhost only. It can read any folder you point it at and has **no authentication**, so don't expose it to a network.

### Tests

```bash
pytest -v
```

Tests run against temporary folders and databases, never your real library.

## How it works

```
frontend (planned) ──HTTP/JSON──▶  backend/api   (FastAPI, thin)  ──▶  backend/core  (engine)
command line (main.py) ───────────────────────────────────────────▶  backend/core
```

`backend/core` contains all the logic and knows nothing about HTTP or the terminal. The CLI and the API are thin front doors onto it, which keeps each layer replaceable.

**Change detection** (`check_state`) compares a snapshot of the disk with the database in three passes: match by path (unchanged or modified), then match the leftover database paths against new files by content hash (renames and moves), and whatever remains is removed or new. `apply_changes` then updates the database; a rename is a path update on the same row, so tags survive.

**Data model** (SQLite, see `backend/core/schema.sql`):

- `assets`: one row per file (path, media type, content hash, size, modified time, metadata)
- `tags`: unique `(namespace, value)` pairs
- `asset_tags`: links between assets and tags

### Project structure

```
MediaAtlas/
├── main.py                  # command-line interface
├── backend/
│   ├── config.py            # paths and settings
│   ├── api/app.py           # FastAPI application
│   └── core/
│       ├── db.py            # database access functions
│       ├── scanner.py       # change detection and applying changes
│       ├── tagging.py       # folder-based tag proposals
│       ├── utils.py         # hashing, media type, tag parsing
│       └── schema.sql       # database schema
├── tests/
├── assets/sample_files/     # sample data for trying things out
└── docs/
```

### Design decisions

| Decision | Choice | Why |
|---|---|---|
| Storage | One SQLite database at the top level | Doesn't alter the filesystem; no server to run; a single file to back up |
| Backend | Python + FastAPI | Quick to build and change; automatic API docs; the core can later move hot spots to optimized libraries or native code behind the same functions |
| Frontend | HTML/CSS + a small JS library, no build step (planned) | Keeps the UI easy to read and change; it only knows the JSON API, so it can be replaced later |
| File identity | Content hash + stable internal ID | Renames and moves don't lose tags |
| Deletions | Missing files stay in the database unless you pass `--delete-removed` | An unplugged drive shouldn't wipe your tags |

## Known limitations

- A file that is edited **and** renamed between scans is seen as removed plus new, so it loses its tags
- Empty files all share one hash and can be mistaken for renames
- Every scan re-hashes every file (skipping unchanged files is planned)
- Paths are stored as absolute paths, so moving a whole library to another location needs a rescan
- Tags attach to files only, not directories (yet)
- No authentication; local use only

## Roadmap

- [x] Database schema, data access layer, hashing
- [x] Change detection and applying changes (renames keep identity and tags)
- [x] Tagging, tag queries, folder-based tag proposals
- [x] Command-line interface
- [x] HTTP API with interactive docs
- [ ] **Web interface**: browse files, filter by tag, add and remove tags
- [ ] API tests, tests for folder tagging
- [ ] Skip hashing unchanged files (size and modified time)
- [ ] Directory tagging and a directory dashboard
- [ ] Missing-file status, search by name and media type, file previews
- [ ] Rename and move files from the app (updating the database, keeping tags)
- [ ] Metadata extraction, thumbnails, workflow profiles
- [ ] Performance: faster hashing, parallel scans, then native code where profiling says it's needed

## Contributing

This is a personal learning project and not currently set up for outside contributions, but issues and suggestions are welcome.

## License

MIT, see [LICENSE](LICENSE).
