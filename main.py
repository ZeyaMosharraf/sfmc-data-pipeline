import json
import time
from pathlib import Path
from config.settings import load_settings
from clients.sfmc_client import get_token, fetch
from transform.extract import transform
from state.checkpoint import load_checkpoint, save_checkpoint, clear_checkpoint
from utils.logger import get_logger

logger = get_logger(__name__)


def run_fetch_data():
    output_path = Path("output/sfmc_assets.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    settings = load_settings()
    token = get_token()

    page, last_id = load_checkpoint() 

    total_processed = 0
    all_excel_rows = []
    
    if output_path.exists():
        with open(output_path, "r", encoding="utf-8") as f:
            all_excel_rows = json.load(f)
        logger.info(f"📂 Resumed — loaded {len(all_excel_rows)} existing records")
    
    start_time = time.time()
    logger.info(f"🚀 Starting fetch from page: {page}, last_id: {last_id}")

    while True:
        items, next_page = fetch(token, page=page)

        if not items:
            logger.info("✅ No more items to process.")
            break

        excel_rows, _ = transform(items)
        all_excel_rows.extend(excel_rows)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(all_excel_rows, f, indent=2, ensure_ascii=False)

        total_processed += len(excel_rows)

        current_last_id = excel_rows[-1]["id"] if excel_rows else last_id
        save_checkpoint(next_page or page, current_last_id)

        logger.info(f"📦 Page {page} — {len(excel_rows)} rows | last_id: {current_last_id} | next: {next_page}")

        if not next_page:
            logger.info("✅ Reached last page.")
            clear_checkpoint()
            break

        page = next_page

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_excel_rows, f, indent=2, ensure_ascii=False)

    end_time = time.time()
    elapsed = end_time - start_time

    logger.info("===== FETCH SUMMARY =====")
    logger.info(f"Total processed: {total_processed}")
    logger.info(f"Unique records: {len(all_excel_rows)}")
    logger.info(f"Output saved to: {output_path}")
    logger.info(f"Total time: {elapsed:.2f} seconds")
    logger.info(f"Records per second: {total_processed / elapsed:.2f}")
    logger.info("✅ Fetch completed successfully.")


if __name__ == "__main__":
    run_fetch_data()