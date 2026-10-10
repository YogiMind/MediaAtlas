# Ideas

Nothing here is promised. When you decide to build something, move it to
[roadmap.md](roadmap.md) and record the design choice in [decisions.md](decisions.md).

## Primary use case: folk music recordings

**Status: Idea (drives the roadmap).**

Several hundred audio recordings, mostly made on a phone: jam tunes, concerts,
my own compositions with many takes, and traditional dance tunes (polska,
walz, schottis, ...) from specific regions or learned from specific people. A folder
tree can only express one of these categories at a time, but I want to ask
different questions on different days:

- "All the good jam tunes"
- "Everything from one region"
- "Only good-quality recordings"
- "All takes of one composition, in order"

### Pipeline

```
phone ──(new recordings)──▶ INBOX ──▶ MediaAtlas library (source of truth, computer)
                                              │
                            profile: "good jam tunes", "polskas by region", ...
                                              ▼
phone ◀──(generated folder structure)── EXPORT folder
```

- The **computer** holds the library and does all the work. The phone is a
  recorder on one side and a plain file player on the other. No mobile app, no
  database sync, and no merge conflicts because each direction is one-way.
- The **master library stays stable** (flat, or sorted by import date) and
  MediaAtlas never reorganizes it. Folder structures are *generated exports*:
  disposable copies built from tags. One recording can appear in a by-region
  export on Monday and a by-tune-type export on Friday.
- **The export is read-only.** Edits happen only in MediaAtlas; renaming or
  deleting files on the phone does not flow back.

### Moving files between phone and computer

The app needs no phone integration; it reads an inbox folder and writes an
export folder, and something else moves those folders.

- **Syncthing** (Pixel 7 Pro and Arch): continuous, direct sync with no cloud.
  Android folder set to *send only* for new recordings, a second folder set to
  *receive only* for the export. On Android, use a maintained build
  (Syncthing-Fork); the original app was discontinued. On Arch, `syncthing` is
  in the official repositories.
- **USB cable / `adb`**: manual but dependable fallback.
- **Open question:** where does the phone's recording app save files? Some apps
  keep recordings inside the app instead of a normal folder, in which case they
  must be exported first, or a different recorder used. Check before designing
  the inbox step.

### Bootstrapping from the existing folders

The current mixed organization (some by region, some by jam / concert /
composed) already contains tagging information. `propose_folder_tags` can
turn folder names into tags, but today it puts them all in one `folder`
namespace.

Idea: let the review step **map each folder name to a namespace**, e.g.
`dalarna → region:dalarna`, `jam → context:jam`, `concert → context:concert`.
The user edits the proposal once, applies it, and several hundred recordings
are roughly tagged without hand-tagging each. Files that still lack a tag
(for example, no tune type) show up as a to-do list.

## Tags

**Status: namespaced tags are implemented; the rest is Idea.**

Different tags could carry different weight:

- **Free tags**, set by the user (implemented as the `tag` namespace)
- **Predefined tags**, a controlled vocabulary
- **Namespaced tags**, e.g. `genre:folk` + `context:concert` (implemented)
- **Structure tags**, which affect how files are arranged, not only labelled

Open: should namespaces have a type (free / predefined / structural), and where would that be stored?

### A starting scheme for the music library

| Namespace | Examples | Notes |
|---|---|---|
| `type` | `polska`, `waltz`, `polka` | The dance form |
| `region` | (the regions I use) | Where the tune comes from |
| `source` | a person's name | Who it was learned from |
| `context` | `jam`, `concert`, `composing`, `practice` | The occasion |
| `work` | a song title | Groups the takes of one composition |
| `take` | `1`, `2`, `3` | Order within a work |
| `rating` | `1` to `5` | Quality of the *performance* |

**Performance quality and audio quality are different questions.** A rating is
a judgement made by listening. Audio quality (sample rate, bitrate, noise) is
mostly measurable from the file, so it belongs under metadata and can be
filtered without manual tagging.

Open:
- Is `take` a tag, or a number stored on the asset? Ordering by a tag value
  needs a numeric sort, which tags don't give for free.
- Should a recording be allowed several values in one namespace (a tune with
  two `source` people, or two `region` values)?

## Workflow profiles

A preset for one use case (e.g. "polskas by region", "good jam tunes",
"composition takes"). Concretely, a profile is **a query plus a layout**:

```json
{
  "name": "polskas-by-region",
  "include": ["type:polska"],
  "exclude": ["rating:1"],
  "layout": "{region}/{source}"
}
```

- `include` / `exclude`: which assets are selected (all `include` tags
  required; none of the `exclude` tags allowed)
- `layout`: a folder template filled in from each asset's tag values; assets
  missing a tag used in the template go to an `unsorted` folder
- Possible extras: a filter on extracted metadata (e.g. "only high-quality
  audio"), a sort order, a file-name template

Stored as plain JSON files at first; a database table only if profiles need to
be edited from the UI.

Open: is a profile just a saved query plus a view? See *Views* below.

## Export to a generated folder structure

**Status: Idea (central to the use case).**

Build a folder tree from a profile and copy the selected files into it.

- **Plan first, then execute.** A pure function returns a list of
  `(source, destination)` pairs and touches nothing, like `propose_folder_tags`.
  That makes it easy to review and to test. A separate step performs the copies.
- **Copies, not links.** Phones and sync tools generally don't handle symlinks
  or hardlinks.
- **Manifest for incremental sync.** Record what was exported (source,
  destination, hash). The next export copies only what changed and removes
  files that no longer belong to the profile. Without a manifest, every export
  is a full re-copy.
- **Naming.** Phone recordings tend to be named like `Recording 123`. The
  layout needs a collision rule (date prefix or numeric suffix), and perhaps a
  file-name template such as `{date} {type} {source}`.
- **Tags in the copies.** A phone player can't see MediaAtlas tags. Writing tags
  into the *copies'* own metadata (title, artist, genre) lets the player browse
  by them without touching the originals. Alternative: generate `.m3u` playlists.
- **Never scan the export folder into the library.** The copies have identical
  hashes and would appear as duplicates. Scans should only cover configured
  library roots.

## Views

A view might be three things:

- **A query** (which files)
- **A grouping rule** (how they are arranged, e.g. by album, then track number)
- **A presentation hint** (list, grid, tree)

Possible work: a view schema, an execution engine, grouping logic.

A profile's `include`/`exclude` is the query and its `layout` is the grouping
rule, so a view for the UI and an export layout may be the same thing viewed in
two places. Worth keeping them as one concept.

Related: selecting a category could keep a virtual directory structure, so
files are worked with in a layout suited to the current use case, without moving
anything on disk ("don't fight the filesystem").

## Fast tagging and listening (frontend)

**Status: Idea.** With hundreds of recordings, tagging one file at a time
through the CLI would be painful, so the first useful UI is probably:

- An audio player for the selected recording (via `/api/assets/{id}/file`;
  needs range-request support for seeking)
- A "next untagged recording" queue
- Keyboard-driven tagging and rating while a recording plays
- Select several files and apply one tag to all of them
- A view of recordings missing a tag in a given namespace (e.g. "no `type` yet")

Open: which audio formats will the browser play (the phone's recording format
matters), and is transcoding to a browser-friendly format ever needed?

## Categorization questions

What a good tagging scheme should answer:

- What rough category is this file?
- What is its use case?
- What is its quality? (performance rating vs measured audio quality)
- Does it belong to an album or a composition (name, order number)? (`work` + `take`)
- What does "same file" mean? (Duplicates are currently content-hash matches; near-duplicates, such as the same recording at two bitrates or an edited trim of one recording, are not handled.)

## Extra functionality

- Notes on a file (e.g. where a tune was learned, what's unusual about it)
- Links between files (sheet music + audio)
- File versioning for production work
- Move and rename files in the master library from the app (riskier than exports; needs a safety design)

## Metadata per media type

**Status: Idea.** The `assets.metadata` column exists (JSON) but is currently empty. See the proposed approach in [decisions.md](decisions.md).

- **All files:** type (extension or MIME), date (which date? configurable?), path, hash
- **Audio:** duration, title, artist, sample rate, bitrate, channels, container/codec
  (extractable with a library such as `mutagen`)
- **Image:** resolution
- **Video:** duration, resolution, frame rate, codec

**Recording date matters.** For takes, concerts, and chronology, the date a tune
was recorded is valuable, but copying files often resets the modified time.
Capture the original date at first import (from the file, its embedded
metadata, or its name) and store it in `metadata`, rather than trusting mtime
later.

Open: which of these can be extracted automatically, and which must be entered by the user?

## Core concepts per media type

- **Audio recordings:** the main use case, see above. Still to decide: how to
  handle a long recording that contains several tunes (one asset or several?).
- **Photo:** _to be designed_
- **Video:** _to be designed_

## Other platforms

**Status: parked.** The phone does not need to run MediaAtlas (see pipeline
above). If a browser-based UI is wanted on the phone, it can reach the
computer's server over a private network (e.g. Tailscale) once authentication
and restricted library roots exist. A standalone phone app is a separate
project.

Cheap choices that keep options open: store paths relative to a library root,
keep the frontend on relative URLs, and keep `core` free of I/O assumptions.

## Open problems

- A file that is **edited and renamed** between scans loses its identity (looks like removed + new). Possible fix: fuzzy matching on size, modified time, and name similarity.
- Directory tagging: separate `directories` table, or directories as assets?
- Whether identity should be re-anchored after a content edit (new hash, same asset).
- A recording trimmed or re-encoded after import gets a new hash. Does it become a new asset, or a "version" of the old one?
- Tags in several namespaces with multiple values (see *Tags*) versus a simple one-value-per-namespace rule.
