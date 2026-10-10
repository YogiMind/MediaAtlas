# Ideas

Nothing here is promised. When you decide to build something, move it to
[roadmap.md](roadmap.md) and record the design choice in [decisions.md](decisions.md).

## Tags

**Status: namespaced tags are implemented; the rest is Idea.**

Different tags could carry different weight:

- **Free tags**, set by the user (implemented as the `tag` namespace)
- **Predefined tags**, a controlled vocabulary
- **Namespaced tags**, e.g. `genre:folk` + `context:concert` (implemented)
- **Structure tags**, which affect how files are arranged, not only labelled

Open: should namespaces have a type (free / predefined / structural), and where would that be stored?

## Workflow profiles

A preset of tag combinations, view settings, and default tags for one use case
(e.g. "mixing session" vs "photo culling"). Switching profile changes what you
see and how it is grouped.

Open: is a profile just a saved query plus a view? See *Views* below.

## Views

A view might be three things:

- **A query** (which files)
- **A grouping rule** (how they are arranged, e.g. by album, then track number)
- **A presentation hint** (list, grid, tree)

Possible work: a view schema, an execution engine, grouping logic.

Related: selecting a category could keep a virtual directory structure, so
files are worked with in a layout suited to the current use case, without moving
anything on disk ("don't fight the filesystem").

## Categorization questions

What a good tagging scheme should answer:

- What rough category is this file?
- What is its use case?
- What is its quality?
- Does it belong to an album (name, order number)?
- What does "same file" mean? (Duplicates are currently content-hash matches; near-duplicates, such as the same recording at two bitrates, are not handled.)

## Extra functionality

- Notes on a file
- Links between files (sheet music + audio)
- File versioning for production work
- Export files by tag

## Metadata per media type

**Status: Idea.** The `assets.metadata` column exists (JSON) but is currently empty. See the proposed approach in [decisions.md](decisions.md).

- **All files:** type (extension or MIME), date (which date? configurable?), path, hash
- **Audio:** duration, title, artist, ...
- **Image:** resolution
- **Video:** duration, resolution, frame rate, codec

Open: which of these can be extracted automatically, and which must be entered by the user?

## Core concepts per media type

_Placeholders; fill in when designing each workflow._

- **Audio recordings:** ...
- **Photo:** ...
- **Video:** ...

## Open problems

- A file that is **edited and renamed** between scans loses its identity (looks like removed + new). Possible fix: fuzzy matching on size, modified time, and name similarity.
- Directory tagging: separate `directories` table, or directories as assets?
- Whether identity should be re-anchored after a content edit (new hash, same asset).
