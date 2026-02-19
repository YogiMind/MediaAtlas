from pathlib import Path
import os

# Create tag-groups based on directory structure. 
# Offer possibility to change tag names before applying
def generate_tags(conn, dir):
    tags = {}
    for root, dirs, files in os.walk(dir):
        rname = Path(root).name
        for tag in dirs:
            print(tag)
            tags.update({tag: []})
        if rname in tags.keys():
            tags[rname] += files

    print(tags)


