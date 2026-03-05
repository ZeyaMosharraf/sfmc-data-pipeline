import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from config.settings import load_settings
from config.sfmc_columns import sfmc_properties
from utils.logger import get_logger

logger = get_logger(__name__)

_session = None
_credentials = None
_token = None
_token_expiry = 0

def get_sfmc_session() -> requests.Session:
    global _session
    if _session is None:
        _session = requests.Session()

        retry_strategy = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST", "OPTIONS"]  # POST needed for fetch() and get_token()
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        _session.mount("https://", adapter)
        _session.mount("http://", adapter)
    return _session

def get_credentials():
    """Load and cache credentials once to avoid repeated .env reads per page."""
    global _credentials
    if _credentials is not None:
        return _credentials

    settings = load_settings()

    client_id = settings.get("SFMC_CLIENT_ID")
    if not client_id:
        raise RuntimeError("client_id is missing")

    client_secret = settings.get("SFMC_CLIENT_SECRET")
    if not client_secret:
        raise RuntimeError("client_secret is missing")

    subdomain = settings.get("SFMC_SUBDOMAIN")
    if not subdomain:
        raise RuntimeError("subdomain is missing")

    page_size = settings.get("PAGE_SIZE")
    if not page_size:
        raise RuntimeError("page_size is missing")

    _credentials = (client_id, client_secret, subdomain, int(page_size))
    return _credentials

def get_token():
    """Return a cached token, refreshing it 60 seconds before expiry."""
    global _token, _token_expiry

    if _token and time.time() < _token_expiry - 60:
        return _token

    client_id, client_secret, subdomain, page_size = get_credentials()
    session = get_sfmc_session()

    url = f"https://{subdomain}.auth.marketingcloudapis.com/v2/token"

    r = session.post(
        url,
        json={
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret
        },
        timeout=30
    )
    r.raise_for_status()
    data = r.json()
    _token = data["access_token"]
    expires_in = data.get("expires_in", 1200)
    _token_expiry = time.time() + expires_in
    logger.info("🔑 Token refreshed, valid for %ss", expires_in)
    return _token

def fetch(token, page=1):
    client_id, client_secret, subdomain, page_size = get_credentials()

    session = get_sfmc_session()

    url = f"https://{subdomain}.rest.marketingcloudapis.com/asset/v1/content/assets/query"
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "page": {
            "page": page,
            "pageSize": page_size
        },
        "sort": [
            {
                "property": "id",
                "direction": "ASC"
            }
        ]
    }

    r = session.post(
        url,
        headers={**headers, "Content-Type": "application/json"},
        json=payload,
        timeout=30
    )

    logger.info(f"Response status: {r.status_code} — page {page}")
    if r.status_code != 200:
        logger.error(f"❌ Error response: {r.json()}")
    r.raise_for_status()
    items = r.json().get("items", [])
    next_page = page + 1 if len(items) == int(page_size) else None
    return items, next_page