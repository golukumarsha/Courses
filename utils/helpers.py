import json

DATA_FILE = "course.json"


def read_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []


def write_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)
