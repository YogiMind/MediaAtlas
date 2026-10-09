from pathlib import Path
from backend.core.db import *


def propose_folder_tags(root):
    """Suggest tags for every file based on the folders it sits in.

    Each file gets one tag per folder between `root` and the file, so
    root/Rock/Live/song.wav is proposed for both "Rock" and "Live".
    Folders with the same name in different places share one tag
    (e.g. every "drums" folder -> tag "drums").

    Nothing is written to the database; the result is a proposal the
    user can review and rename before applying it.

    Args:
        root: Directory that was scanned. Folders above it are ignored.

    Returns:
        dict mapping tag name -> list of full file paths (as strings,
        matching the paths stored in the assets table).
    """
    root = Path(root)
    proposal = {}

    for p in root.rglob("*"):
        if not p.is_file():
            continue
        # Folder names between root and the file, e.g. ("Rock", "Live")
        for folder in p.relative_to(root).parent.parts:
            proposal.setdefault(folder, []).append(str(p))

    return proposal


def apply_tag_proposal(conn, proposal, namespace="folder", renames=None):
    """Write a (possibly edited) tag proposal to the database.

    Files must already be imported (present in the assets table);
    paths with no matching asset are skipped.

    Args:
        conn: Open sqlite3 connection (caller commits).
        proposal: Output of propose_folder_tags().
        namespace: Namespace for the created tags, e.g. "folder:Rock".
        renames: Optional {old_name: new_name} to rename tags first.
    """
    renames = renames or {}

    for name, paths in proposal.items():
        tag_id = get_or_create_tag(conn, namespace, renames.get(name, name))
        for path in paths:
            asset = get_by_path(conn, path)
            if asset:
                add_asset_tag(conn, asset[0]["id"], tag_id)

