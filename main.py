import json
import time
from pathlib import Path
import token
from config.settings import load_settings
from clients.sfmc_client import get_token, rest_fetch
from clients.sfmc_soap_client import soap_fetch
from transform.extract import transform
from transform.soap_extract import soap_extract
from state.checkpoint import load_checkpoint, save_checkpoint, clear_checkpoint
from utils.logger import get_logger

logger = get_logger(__name__)


def run_fetch_rest_data():
    output_path = Path("output/sfmc_html.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    settings = load_settings()
    token = get_token()

    page, last_id = load_checkpoint() 

    checkpoint = load_checkpoint("rest_checkpoint.json")
    page = checkpoint.get("page", 1) if checkpoint else 1
    last_id = checkpoint.get("last_id", None) if checkpoint else None

    total_processed = 0
    all_html_rows = []
    
    if output_path.exists():
        with open(output_path, "r", encoding="utf-8") as f:
            all_html_rows = json.load(f)
        logger.info(f"📂 Resumed — loaded {len(all_html_rows)} existing records")
    
    start_time = time.time()
    logger.info(f"🚀 Starting fetch from page: {page}, last_id: {last_id}")

    while True:
        items, next_page = rest_fetch(token, page=page)

        if not items:
            logger.info("✅ No more items to process.")
            break

        _, html_rows = transform(items)
        all_html_rows.extend(html_rows)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(all_html_rows, f, indent=2, ensure_ascii=False)

        total_processed += len(html_rows)

        current_last_id = html_rows[-1]["id"] if html_rows else last_id


        save_checkpoint(next_page or page, current_last_id)
        save_checkpoint("rest_checkpoint.json", {"page": next_page or page, "last_id": current_last_id})

        logger.info(f"📦 Page {page} — {len(html_rows)} rows | last_id: {current_last_id} | next: {next_page}")

        if not next_page:
            logger.info("✅ Reached last page of REST API.")
            clear_checkpoint("rest_checkpoint.json")
            break

        page = next_page

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_html_rows, f, indent=2, ensure_ascii=False)

    end_time = time.time()
    elapsed = end_time - start_time

    logger.info("===== FETCH SUMMARY REST API =====")
    logger.info(f"Total processed: {total_processed}")
    logger.info(f"Unique records: {len(all_html_rows)}")
    logger.info(f"Output saved to: {output_path}")
    logger.info(f"Total time: {elapsed:.2f} seconds")
    logger.info(f"Records per second: {total_processed / elapsed:.2f}")
    logger.info("✅ Fetch completed successfully.")


def run_fetch_soap_data():
    output_path = Path("output/sfmc_soap.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    

    checkpoint = load_checkpoint("soap_checkpoint.json")
    request_id = checkpoint.get("request_id", None) if checkpoint else None

    total_processed = 0
    all_email_tracking_rows = []
    
    if output_path.exists():
        with open(output_path, "r", encoding="utf-8") as f:
            all_email_tracking_rows = json.load(f)
        logger.info(f"📂 Resumed — loaded {len(all_email_tracking_rows)} existing records")
    
    start_time = time.time()
    logger.info(f"🚀 Starting fetch from request_id: {request_id}")

    while True:
        
        results, request_id, has_more = soap_fetch(continue_request=request_id)

        if not results:
            logger.info("✅ No more items to process in SOAP API.")
            break

        soap_result = soap_extract(results)
        all_email_tracking_rows.extend(soap_result)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(all_email_tracking_rows, f, indent=2, ensure_ascii=False)

        total_processed += len(soap_result)

        save_checkpoint("soap_checkpoint.json", {"request_id": request_id})

        logger.info(f"📦 Batch fetched — {len(soap_result)} rows | request_id: {request_id} | has_more: {has_more}")

        if not has_more:
            logger.info("✅ Reached last page of SOAP API.")
            clear_checkpoint("soap_checkpoint.json")
            break

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_email_tracking_rows, f, indent=2, ensure_ascii=False)
    logger.info(f"Unique records: {len(all_email_tracking_rows)}")

    end_time = time.time()
    elapsed = end_time - start_time

    logger.info("===== FETCH SUMMARY SOAP API =====")
    logger.info(f"Total processed: {total_processed}")
    logger.info(f"Unique records: {len(all_email_tracking_rows)}")
    logger.info(f"Output saved to: {output_path}")
    logger.info(f"Total time: {elapsed:.2f} seconds")
    logger.info(f"Records per second: {total_processed / elapsed:.2f}")
    logger.info("✅ Fetch completed successfully.")


if __name__ == "__main__":
    run_fetch_soap_data()