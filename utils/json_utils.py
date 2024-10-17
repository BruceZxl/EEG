import json
from pathlib import Path


def json_read(path: Path):
    with open(path, 'r') as fp:
        return json.load(fp)


def json_write(obj, path: Path):
    with open(path, 'w') as fp:
        return json.dump(obj, fp)
