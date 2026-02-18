from pathlib import Path
from backend.db.models import *
from backend.scanner.file_hash import hash_file

def import_files(conn, dir):
    for p in Path(dir).rglob("*"):
        if p.is_file():
            stat = p.stat()
            hash = hash_file(p)
            if path_exists(conn, str(p)):
                print(f"{p.name} is already in database")
                continue
            print(f"Adding {p.name}")
            add_asset(conn, str(p), p.suffix, hash, stat.st_size, stat.st_mtime, {})


# New File - Path not in db
# removed - Path in db, not on disk
# modified - Path in db, hash differs, modified differs
# renamed/moved - Hash in db, path differs
#
# 1: check disk against import db
# 2: Check db against disk
def find_changes(conn, dir):
    for p in Path(dir).rglob("*"):
        if p.is_file():
            file_path = str(p)

            # TODO: Avoid hashing large files by checking modified
            content_hash = hash_file(p)

            db_entry = get_by_path(conn, file_path)
            if db_entry:
                if content_hash != db_entry[0][2]:
                    print(f"Modified: {file_path}")
            else:
                matches = get_by_hash(conn, content_hash)
                for match in matches:
                    print(f"Possible rename: {match[1]} -> {file_path}")
    
    rows = conn.execute("SELECT id, path, content_hash FROM assets").fetchall()
    for row in rows:
        if not Path(row[1]).is_file():
            print(f"{row[1]} not found")
            
def check_state(conn, dir):
    disk_files = {}
    db_files = {}
    new_temp = {}
    state_change = {
        "new": [],      # Path only in disk
        "modified": [], # Path in both, hash differ
        "renamed": [],  # New file with matching hash as file with path only in db
        "removed": []   # Path only in db, no new file with matching hash
    }

    for p in Path(dir).rglob("*"):
        if p.is_file():
            file_path = str(p)
            disk_files[file_path] = hash_file(p)
    
    rows = conn.execute(
        "SELECT id, path, content_hash FROM assets"
    ).fetchall()

    for row in rows:
        db_files[row[1]] = row[2]

    for path, disk_hash in disk_files.items():
        if path in db_files:
            if db_files[path] != disk_hash:
                state_change["modified"].append(path)
            db_files.pop(path)
        else:
            new_temp.setdefault(disk_hash, []).append(path)

    for path, db_hash in db_files.items():
        # remaining paths not in disk
        # if hash in new -> rename
        # else -> removed
        if db_hash in new_temp:
            candidates = new_temp[db_hash]

            new_path = candidates.pop(0)
            state_change["renamed"].append((path, new_path))

            for dup_path in candidates:
                state_change["new"].append(dup_path)
            new_temp.pop(db_hash)
        else:
            state_change["removed"].append(path)

    for paths in new_temp.values():
        state_change["new"].extend(paths)
    
    print(state_change)

