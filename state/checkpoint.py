import json
from pathlib import Path

CHECKPOINT_FILE = Path("state/checkpoint.json")

def save_checkpoint(page: int, last_id: int):
    CHECKPOINT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump({"page": page, "last_id": last_id}, f)

def load_checkpoint():
    if not CHECKPOINT_FILE.exists():
        return 1, None  # page, last_id
    with open(CHECKPOINT_FILE, "r") as f:
        data = json.load(f)
    return data.get("page", 1), data.get("last_id", None)

def clear_checkpoint():
    if CHECKPOINT_FILE.exists():
        CHECKPOINT_FILE.unlink()