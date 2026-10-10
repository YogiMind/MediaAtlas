"""MediaAtlas command-line interface."""
import argparse
import sys
from pathlib import Path

from backend.core.db import (
    connect, get_by_path, get_or_create_tag, add_asset_tag,
    get_assets_by_tags, get_tags_for_asset, list_assets, list_tags,
)
from backend.core.scanner import check_state, apply_changes
from backend.core.tagging import propose_folder_tags, apply_tag_proposal
from backend.core.utils import parse_tag


"""CLI with some commands:
python main.py scan <folder> [--apply]    detect changes, optionally write them to the DB
python main.py list                       show all known files with their tags
python main.py tag <file> mood:dark ...   add tags to a file
python main.py find mood:dark ...         find files that have ALL of these tags
python main.py tags                       list all tags with usage counts
"""


PROJ_DIR = Path(__file__).parent
DEFAULT_DB = PROJ_DIR / "data" / "mediaatlas.db"
SCHEMA = PROJ_DIR / "backend" / "core" / "schema.sql"


# ---------- helpers ----------

def open_db(db_path):
    """Open the database, creating the file and tables if they don't exist."""
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = connect(db_path)
    conn.executescript(SCHEMA.read_text())   # safe to repeat: IF NOT EXISTS
    return conn


def print_changes(changes):
    """Print a check_state() report in a readable form."""
    total = sum(len(v) for v in changes.values())
    if total == 0:
        print("No changes: database matches disk.")
        return
    for path in changes["new"]:
        print(f"  + new       {path}")
    for path in changes["modified"]:
        print(f"  ~ modified  {path}")
    for old, new in changes["renamed"]:
        print(f"  > renamed   {old}\n              -> {new}")
    for path in changes["removed"]:
        print(f"  - removed   {path}")
    print(f"\n{len(changes['new'])} new, {len(changes['modified'])} modified, "
          f"{len(changes['renamed'])} renamed, {len(changes['removed'])} removed")


# ---------- commands ----------

def cmd_scan(args):
    root = Path(args.folder).resolve()
    if not root.is_dir():
        sys.exit(f"Not a folder: {root}")

    with open_db(args.db) as conn:
        changes = check_state(conn, root)
        print_changes(changes)

        if not args.apply:
            print("\nDry run: nothing written. Re-run with --apply to update the database.")
            return

        apply_changes(conn, changes, delete_removed=args.delete_removed)
        if args.folder_tags:
            apply_tag_proposal(conn, propose_folder_tags(root))
        print("\nDatabase updated.")


def cmd_list(args):
    with open_db(args.db) as conn:
        assets = list_assets(conn)
        if not assets:
            print("Database is empty. Try: python main.py scan <folder> --apply")
        for asset in assets:
            tags = ", ".join(f"{t['namespace']}:{t['value']}"
                             for t in get_tags_for_asset(conn, asset["id"]))
            print(f"{asset['path']}  [{tags}]" if tags else asset["path"])


def cmd_tag(args):
    path = str(Path(args.file).resolve())
    with open_db(args.db) as conn:
        rows = get_by_path(conn, path)
        if not rows:
            sys.exit(f"Not in database: {path}\nScan its folder first with --apply.")
        asset_id = rows[0]["id"]
        for namespace, value in args.tags:
            tag_id = get_or_create_tag(conn, namespace, value)
            add_asset_tag(conn, asset_id, tag_id)
            print(f"Tagged {Path(path).name} with {namespace}:{value}")


def cmd_find(args):
    with open_db(args.db) as conn:
        results = get_assets_by_tags(conn, args.tags)
        for row in results:
            print(row["path"])
        print(f"\n{len(results)} file(s) found")


def cmd_tags(args):
    with open_db(args.db) as conn:
        rows = list_tags(conn)
        if not rows:
            print("No tags yet.")
        for row in rows:
            print(f"{row['namespace']}:{row['value']}  ({row['n']})")


# ---------- argument parsing ----------

def build_parser():
    parser = argparse.ArgumentParser(
        prog="mediaatlas",
        description="Organize media by identity and tags, not just folders.",
    )
    parser.add_argument("--db", type=Path, default=DEFAULT_DB,
                        help="database file (default: data/mediaatlas.db); "
                             "must come before the command")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("scan", help="detect changes in a folder")
    p.add_argument("folder")
    p.add_argument("--apply", action="store_true",
                   help="write the changes to the database (default: dry run)")
    p.add_argument("--delete-removed", action="store_true",
                   help="also delete database entries for files missing from disk")
    p.add_argument("--folder-tags", action="store_true",
                   help="also tag files after the folders they sit in")
    p.set_defaults(func=cmd_scan)

    p = sub.add_parser("list", help="show all known files and their tags")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("tag", help="add tags to a file")
    p.add_argument("file")
    p.add_argument("tags", nargs="+", type=parse_tag, help="e.g. mood:dark instrument:guitar")
    p.set_defaults(func=cmd_tag)

    p = sub.add_parser("find", help="find files that have ALL the given tags")
    p.add_argument("tags", nargs="+", type=parse_tag)
    p.set_defaults(func=cmd_find)

    p = sub.add_parser("tags", help="list all tags and how many files use them")
    p.set_defaults(func=cmd_tags)

    return parser


if __name__ == "__main__":
    args = build_parser().parse_args()
    args.func(args)
