import json
from pathlib import Path

def save_checkpoint(filename: str, data: dict):
    path = Path(f"state/{filename}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f)

def load_checkpoint(filename:str) -> dict:
    path = Path(f"state/{filename}")
    if not path.exists():
        return None 
    with open(path, "r") as f:
        data = json.load(f)
    return data

def clear_checkpoint(filename:str):
    path =Path(f"state/{filename}")
    if path.exists():
        path.unlink()