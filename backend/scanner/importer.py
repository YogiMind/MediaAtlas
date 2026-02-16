from pathlib import Path
from db import models
import file_hash

def import_files(conn, dir):
    for p in Path(dir).rglob("*"):
        if p.is_file():
            stat = p.stat()
            hash = file_hash.hash_file(p)
            if models.hash_exists(conn, hash) and models.path_exists(conn, str(p)):
                print(f"{p.name} is already in database")
                continue
            print(f"Adding {p.name}")
            models.add_asset(conn, str(p), p.suffix, hash, stat.st_size, stat.st_mtime, {})


# New File - Path not in db
# removed - Path in db, not on disk
# modified - Path in db, hash differs, modified differs
# renamed/moved - Hash in db, path differs
#
# 1: check disk against import db
# 2: Check db against disk
def find_changes(conn, dir):
    rows = conn.execute("SELECT id, path, content_hash FROM assets").fetchall()
    for p in Path(dir).rglob("*"):
        if p.is_file():
            file_path = str(p)

            # TODO: Avoid hashing large files by checking modified
            hash = file_hash.hash_file(p)

            db_entry = models.get_by_path(conn, file_path)
            if db_entry:
                if file_hash != db_entry[2]:
                    print("Modified")
            else:
                matches = models.get_by_hash(conn, hash)
                for match in matches:
                    print(f"Possible rename: {match[1]} -> {file_path}")
    
        for row in rows:
            pass

