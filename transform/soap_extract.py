from utils.logger import get_logger

logger = get_logger(__name__)

def soap_extract(rows: list[dict]) -> list[dict]:
    soap_extracted = []
    for row in rows:
        clean_row ={}
        for key, value in row.items():
            if value is None:
                clean_row[key] = None
            elif isinstance(value, str):
                clean = value.strip()
                clean_row[key] = clean if clean else None
        soap_extracted.append(clean_row)
    logger.info(f'Extracted {len(soap_extracted)} records')
    return soap_extracted