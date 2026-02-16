import os
import json
from pathlib import Path


DIR = Path("/home/scazarch/Documents/Architecture/Lab3/stuff/")
# DIR = Path(".")
INDENT_STYLE = "  "
DIR_SYMBOL = " "
JSON_PATH = "data.json"


json_data = {}
json_data["root"] = str(DIR)
json_data["content"] = []

for root, dirs, files in os.walk(DIR):
    for dir in dirs[:]:
        if dir.startswith("."):
            print("removing", dir)
            dirs.remove(dir)
        else:
            print("adding", dir)
            json_data["content"].append({
                "name": dir,
                "path": root.replace(str(DIR), ".")
            })


json_string = json.dumps(json_data, indent=4)

if os.path.exists(JSON_PATH):
    file = open(JSON_PATH, "w")
else:
    file = open(JSON_PATH, "x")
file.write(json_string)
print(json_data)
