import json
import csv
from pathlib import Path
from utils.logger import get_logger

logger = get_logger(__name__)

INPUT_FILE = Path("output/sfmc_soap.json")
OUTPUT_FILE = Path("output/sfmc_email_tracking.csv")

COLUMN_MAP = {
    "ID": "ID",
    "EmailName": "Email Name",
    "Subject": "Subject",
    "Status": "Status",
    "SendDate": "Send Date",
    "SentDate": "Sent Date",
    "FromName": "From Name",
    "FromAddress": "From Address",
    "NumberSent": "Number Sent",
    "NumberDelivered": "Number Delivered",
    "UniqueOpens": "Unique Opens",
    "UniqueClicks": "Unique Clicks",
    "HardBounces": "Hard Bounces",
    "SoftBounces": "Soft Bounces",
    "Unsubscribes": "Unsubscribes"
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