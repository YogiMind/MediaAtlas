import os
from pathlib import Path

DIR = Path("/home/scazarch/dotfiles/nvim/.config/nvim")

def scan_dir(path, level):
    indent = "  "*level
    with os.scandir(path) as entries:
        for entry in entries:
            if entry.is_dir():
                print(indent + "/" + entry.name)
                scan_dir(path / entry.name, level + 1)
            else:
                print(indent + entry.name)

scan_dir(DIR, 0)
