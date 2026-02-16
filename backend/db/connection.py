import sqlite3
from pathlib import Path
from scanner import importer

# DIR = Path("/home/scazarch/Pictures")
DIR = Path("/home/scazarch/Documents/Projects/DirectoryDashboard/backend/db/sample_files")
DB = Path("sample.db")

# DB = Path("../db/pics.db")
def main():
    with sqlite3.connect(DB) as conn:
        # # Create tables
        # with open("schema.sql") as f:
        #     conn.executescript(f.read())
        # import_files(conn, DIR)

        # generate_tags(conn, DIR)
        importer.find_changes(conn, DIR)



if __name__ == "__main__":
    main()
