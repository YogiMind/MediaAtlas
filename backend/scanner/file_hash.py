import hashlib

def hash_file(path, algo="sha256", chunk_size=1024*1024):
    h = hashlib.new(algo)
    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
            h.update(chunk)
    return h.hexdigest()
