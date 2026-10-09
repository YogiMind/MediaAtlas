from pathlib import Path

from backend.core.db import connect, get_or_create_tag, add_asset_tag, get_by_path
from backend.core.scanner import check_state, apply_changes

SCHEMA = Path("backend/core/schema.sql")


def make_db(tmp_path):
    conn = connect(tmp_path / "test.db")
    conn.executescript(SCHEMA.read_text())
    return conn


def test_first_scan_finds_everything_new(tmp_path):
    library = tmp_path / "library"
    library.mkdir()
    (library / "a.wav").write_bytes(b"aaa")

    conn = make_db(tmp_path)
    changes = check_state(conn, library)

    assert changes["new"] == [str(library / "a.wav")]
    assert changes["renamed"] == changes["modified"] == changes["removed"] == []


def test_rename_keeps_asset_id_and_tags(tmp_path):
    library = tmp_path / "library"
    library.mkdir()
    (library / "a.wav").write_bytes(b"aaa")

    conn = make_db(tmp_path)
    apply_changes(conn, check_state(conn, library))
    asset_id = get_by_path(conn, str(library / "a.wav"))[0]["id"]
    add_asset_tag(conn, asset_id, get_or_create_tag(conn, "mood", "dark"))

    (library / "a.wav").rename(library / "b.wav")
    changes = check_state(conn, library)
    assert changes["renamed"] == [(str(library / "a.wav"), str(library / "b.wav"))]

    apply_changes(conn, changes)
    moved = get_by_path(conn, str(library / "b.wav"))[0]
    assert moved["id"] == asset_id
    assert conn.execute(
        "SELECT COUNT(*) FROM asset_tags WHERE asset_id=?", (asset_id,)
    ).fetchone()[0] == 1


def test_duplicate_files_both_renamed(tmp_path):
    """Regression test for the duplicate-hash bug in check_state."""
    library = tmp_path / "library"
    library.mkdir()
    (library / "x1.wav").write_bytes(b"same")
    (library / "x2.wav").write_bytes(b"same")

    conn = make_db(tmp_path)
    apply_changes(conn, check_state(conn, library))

    (library / "x1.wav").rename(library / "y1.wav")
    (library / "x2.wav").rename(library / "y2.wav")

    changes = check_state(conn, library)
    assert len(changes["renamed"]) == 2
    assert changes["removed"] == [] and changes["new"] == []

def test_scanning_one_folder_ignores_assets_from_another(tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    a.mkdir(); b.mkdir()
    (a / "one.wav").write_bytes(b"one")
    (b / "two.wav").write_bytes(b"two")

    conn = make_db(tmp_path)
    apply_changes(conn, check_state(conn, a))
    apply_changes(conn, check_state(conn, b))

    # Scanning b must not report a's files as removed
    assert check_state(conn, b)["removed"] == []
    assert check_state(conn, a)["removed"] == []
