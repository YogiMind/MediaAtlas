import hashlib

def hash_file(path, algo="sha256", chunk_size=1024 * 1024):
    """Return the hex digest of a file's contents.

    The file is read in chunks so large media files never have to fit
    in memory. Two files with identical bytes always get the same hash,
    regardless of name or location, which is what MediaAtlas uses as the
    file's content identity.

    Args:
        path: Path (str or Path) of the file to hash.
        algo: Any algorithm name hashlib supports ("sha256", "blake2b", ...).
        chunk_size: Bytes read per iteration (default 1 MB).

    Returns:
        Hex string such as "9f86d081...".

    Raises:
        OSError: If the file can't be opened (missing, permission denied).
    """
    h = hashlib.new(algo)
    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):   # stops when read() returns b""
            h.update(chunk)
    return h.hexdigest()


import mimetypes

def guess_media_type(path):
    """Return a broad media type ("audio", "image", "video", ...) from the file name."""
    mime, _ = mimetypes.guess_type(path)
    return mime.split("/")[0] if mime else "other"


def parse_tag(text):
    """Turn "mood:dark" into ("mood", "dark"). A bare "dark" becomes ("tag", "dark").

    Used as an argparse `type=`, so bad input produces a normal error message.
    Tags are lowercased so "Mood:Dark" and "mood:dark" are the same tag.
    """
    namespace, sep, value = text.partition(":")
    if not sep:                       # no colon given
        namespace, value = "tag", text
    namespace, value = namespace.strip().lower(), value.strip().lower()
    if not namespace or not value:
        raise ValueError(f"invalid tag: {text!r} (use namespace:value)")
    return namespace, value


