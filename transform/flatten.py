import json
import csv
from pathlib import Path
from utils.logger import get_logger

logger = get_logger(__name__)

INPUT_FILE = Path("output/sfmc_assets.json")
OUTPUT_FILE = Path("output/sfmc_assets.csv")

COLUMN_MAP = {
    "id": "ID",
    "name": "Name",
    "views.subjectline.content": "Subject Line",
    "views.preheader.content": "Preheader",
}

def flatten():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    rows = []
    for item in data:
        row = {COLUMN_MAP[k]: item.get(k) for k in COLUMN_MAP}
        rows.append(row)

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(COLUMN_MAP.values()))
        writer.writeheader()
        writer.writerows(rows)

    logger.info(f"✅ Saved {len(rows)} records to {OUTPUT_FILE}")


if __name__ == "__main__":
    flatten()