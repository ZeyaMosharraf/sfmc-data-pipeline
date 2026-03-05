from dotenv import load_dotenv
import os

load_dotenv(override=True)

def load_settings():
    return {
        "SFMC_CLIENT_ID": os.getenv("SFMC_CLIENT_ID"),
        "SFMC_CLIENT_SECRET": os.getenv("SFMC_CLIENT_SECRET"),
        "SFMC_SUBDOMAIN": os.getenv("SFMC_SUBDOMAIN"),
        "PAGE_SIZE": int(os.getenv("PAGE_SIZE", 50))
    }
