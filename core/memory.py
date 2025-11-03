import json
import os

MEMORY_FILE = "context_memory.json"

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {}
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)

def save_memory(data):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=2)

def detect_changes(old, new):
    """Compare old vs new commit state."""
    added = [sha for sha in new if sha not in old]
    updated = [sha for sha in new if sha in old and new[sha]["status"] != old[sha]["status"]]
    return added, updated
