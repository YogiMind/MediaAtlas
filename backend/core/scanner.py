from pathlib import Path
from backend.core.db import *
from backend.core.utils import *

            
def check_state(conn, root):
    """Compare files on disk against the database and classify the changes.

    Files are matched by path first. Paths that exist only on one side are
    then matched by content hash, so a moved or renamed file is reported as
    a rename instead of a removal plus a new file.

    Args:
        conn: Open sqlite3 connection to the MediaAtlas database.
        root: Directory to scan (searched recursively).

    Returns:
        dict with keys "new", "modified", "renamed", "removed".
        "renamed" holds (old_path, new_path) tuples; the others hold paths.
    """
    disk_files = {}   # path -> hash, for every file currently on disk
    db_files = {}     # path -> hash, for every file the DB knows about
    new_temp = {}     # hash -> [paths]: disk files with an unknown path,
                      # held back in case they turn out to be renames
    state_change = {
        "new": [],       # Path only on disk
        "modified": [],  # Path in both, hash differs
        "renamed": [],   # Path only in DB, and a new disk file has the same hash
        "removed": [],   # Path only in DB, and no disk file has that hash
    }

    # --- Snapshot 1: what is on disk right now ---
    for p in Path(root).rglob("*"):
        if p.is_file():
            disk_files[str(p)] = hash_file(p)

    # --- Snapshot 2: what the database remembers ---
    rows = conn.execute(
        "SELECT id, path, content_hash FROM assets"
    ).fetchall()
    for row in rows:
        db_files[row[1]] = row[2]   # row[1] = path, row[2] = content_hash

    # --- Pass 1: compare by path ---
    for path, disk_hash in disk_files.items():
        if path in db_files:
            # Known path: same content or edited?
            if db_files[path] != disk_hash:
                state_change["modified"].append(path)
            # Explained, so remove it. Whatever stays in db_files afterwards
            # is a path the DB knows that is missing from disk.
            db_files.pop(path)
        else:
            # Unknown path: might be new, might be a rename. Decide later.
            new_temp.setdefault(disk_hash, []).append(path)

    # --- Pass 2: explain the DB paths that are missing from disk ---
    for path, db_hash in db_files.items():
        if db_hash in new_temp:
            new_path = new_temp[db_hash].pop(0)
            state_change["renamed"].append((path, new_path))
            if not new_temp[db_hash]:      # remove the key only once it's empty
                del new_temp[db_hash]

        else:
            # Nothing on disk matches: the file is gone.
            state_change["removed"].append(path)

    # --- Pass 3: leftovers in new_temp matched nothing -> genuinely new ---
    for paths in new_temp.values():
        state_change["new"].extend(paths)

    return state_change


def apply_changes(conn, state_change, delete_removed=False):
    """Update the database to match a report from check_state().

    Args:
        conn: Open sqlite3 connection (caller commits).
        state_change: Dict returned by check_state().
        delete_removed: If False (default), files missing from disk are left
            in the database. This protects tags if a drive is merely
            unplugged. Set True to delete them (and their tags).
    """
    # Renames first: the asset keeps its id, so its tags survive.
    for old_path, new_path in state_change["renamed"]:
        update_path(conn, old_path, new_path)

    # Edited files: same asset, new hash/size/mtime.
    for path in state_change["modified"]:
        stat = Path(path).stat()
        update_file_info(conn, path, hash_file(path), stat.st_size, stat.st_mtime)

    # Brand new files.
    for path in state_change["new"]:
        p = Path(path)
        stat = p.stat()
        add_asset(conn, path, guess_media_type(path),
                  hash_file(p), stat.st_size, stat.st_mtime, {})

    if delete_removed:
        for path in state_change["removed"]:
            remove_asset(conn, path)
