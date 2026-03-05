from config.sfmc_columns import sfmc_properties, sfmc_html_properties
from utils.logger import get_logger

logger = get_logger(__name__)

def get_nested(data: dict, path: str):
    keys = path.split(".")
    for key in keys:
        if isinstance(data, dict):
            data = data.get(key)
        else:
            return None
    return data or None 

def clean_text(value: str) -> str | None:
    if not value:
        return None
    return value.strip() or None

def extract_asset(raw: dict) -> dict:
    extracted = {}
    for field in sfmc_properties:
        value = get_nested(raw, field)
        extracted[field] = clean_text(value) if isinstance(value, str) else value
    return extracted

def extract_html(raw: dict) -> dict:
    extracted = {}
    for field in sfmc_html_properties:
        value = get_nested(raw, field)
        extracted[field] = clean_text(value) if isinstance(value, str) else value
    return extracted

def transform(items: list[dict]) -> tuple[list[dict], list[dict]]:
    excel_rows = []
    html_rows = []

    for item in items:
        try:
            excel_rows.append(extract_asset(item))
            html_rows.append(extract_html(item))
        except Exception as e:
            logger.warning(f"⚠️ Skipping item due to error: {e}")
            continue

    logger.info(f"✅ Transformed {len(excel_rows)} items")
    return excel_rows, html_rows