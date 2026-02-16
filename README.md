# MediaAtlas
MediaAtlas is a workflow-oriented media management system that adds semantic structure on top of the filesystem.

Instead of organizing files only by folders, MediaAtlas lets you organize by meaning — using layered identity (hash, path, internal ID), structured tags, and workflow profiles.

Designed for audio, recordings, photos, and production workflows.

## Idea
HTML based interface where you can scan a given path for its directory structure. Dashboard showing the directories with direct links. Should be customizable, add or remove specific directories or even files.
Ability to add tags to files and directories and let you filter for these tags. 


## Architecture overview
Backend (serving ifles, scanning dirs, handling tags) -- Python (Flask or FastAPI?)

Frontend (UI) -- HTML/CSS + JS (Vanilla or React/Vue)

Storage (tags, metadata) -- JSON / SQLite / TinyDB

File system access -- Python os, pathlib, mimetypes

Optional: Thumbnail generation -- Pillow, ffmpeg?

Check NextJS

## Architecture choices
Frontend -- UI, what are the possible frameworks/languages?
- HTML, React JS

Backend -- Python to kick things started, concider changing when app is working

Storage -- Where should tags, media paths etc be stored. What filetype to use? Where do these live, top level or in every directory or both?
- Top level might be prefered to not alter the filesystem itself

API -- What are the interfaces of the frontend, backend etc. Good interface abstraction enables refactoring and improvements later on.

### Communication
- Frontend send HTTP request/response, client-server model?
- Backend returns HTML or JSON
- Frontend displays, filters and updates based on data


## Learning
- Do some basic HTML + CSS
- Learn some JS
- Generate JSON with metadata
- SQL

