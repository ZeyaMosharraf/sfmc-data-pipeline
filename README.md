# SFMC Content Asset Extraction Pipeline
### Digital Marketing Agency | Data Engineering & Migration

---

## Executive Summary

| | |
|---|---|
| **Industry** | Digital Marketing Agency (B2B & Franchise) |
| **Platform** | Salesforce Marketing Cloud (SFMC) |
| **Problem** | Client shutting down SFMC account — all historical content assets at risk of permanent loss |
| **Solution** | Automated Python pipeline using SFMC REST API to extract, transform and preserve all assets before shutdown |
| **Throughput** | ~5.4 records/second |
| **Avg Page Time** | ~9 seconds/page |
| **Output** | Structured JSON + Excel ready for migration or archiving |

---

## Business Problem

The client made the decision to shut down their Salesforce Marketing Cloud account. This created an immediate risk of permanent data loss — years of email content assets including subject lines, preheaders, and full HTML content would become inaccessible once the account was closed.

The challenge was that SFMC does not provide a native bulk export tool for either Content Builder assets or email send tracking data. There was no built-in way to:

- Extract all content assets with structured metadata at scale
- Preserve email content (subject lines, preheaders, HTML) before account closure
- Extract complete email send history (Job IDs, send stats, bounce rates, open rates) via SOAP API
- Produce a clean, structured output ready for archiving or migration to another platform

Manual export was not a viable option given the volume of assets and the time constraint of the account shutdown deadline. An automated extraction pipeline was the only reliable solution.

---

## Solution & Methodology

Built a fully automated Python data pipeline that:

1. **Authenticates** with SFMC using OAuth2 client credentials flow
2. **Fetches** all assets page by page via the POST query endpoint (`/asset/v1/content/assets/query`)
3. **Transforms** raw nested JSON into flat structured rows
4. **Saves** output incrementally to JSON after each page
5. **Checkpoints** progress (page + last ID) so the pipeline resumes automatically if interrupted

### Pipeline Flow

```
SFMC API → Authentication → Paginated Fetch → Transform → Checkpoint → JSON Output → Excel Export
```

### Project Structure

```
sfmc-data-pipeline/
├── main.py                  # Entry point — orchestrates fetch, transform, save
├── clients/
│   ├── __init__.py
│   ├── sfmc_client.py       # REST — Content Builder assets (OAuth2 + POST query)
│   └── sfmc_soap_client.py  # SOAP — Email send tracking (Job IDs, send stats)
├── config/
│   ├── __init__.py
│   ├── settings.py          # Loads environment variables
│   └── sfmc_columns.py      # Defines which fields to extract
├── state/
│   ├── __init__.py
│   └── checkpoint.py        # Saves/loads page + last_id for resume support
├── transform/
│   ├── __init__.py
│   ├── extract.py           # Transforms raw API items into flat rows
│   └── flatten.py           # Helper to flatten nested JSON fields
├── utils/
│   ├── __init__.py
│   └── logger.py            # Centralized logging setup
├── output/                  # Auto-generated — not committed to version control
├── .env                     # Environment variables (not committed)
├── requirements.txt
└── README.md
```

---

## Skills & Technologies

| Skill | Usage |
|---|---|
| **Python** | Core pipeline development |
| **REST API Integration** | SFMC Content Builder API (POST query endpoint) |
| **SOAP API Integration** | SFMC Email Send Tracking (Job IDs, send stats, bounce rates) |
| **OAuth2 Authentication** | SFMC client credentials token flow |
| **Pagination Handling** | Smart stop logic using total count from API response |
| **JSON Transformation** | Nested JSON flattening with dot notation paths |
| **Checkpoint & Resume** | Fault-tolerant pipeline with page + last_id state |
| **Logging** | Structured per-page logging with timestamps |
| **Environment Config** | `.env` based secrets management |

---

## Results & Business Impact

- ✅ **Zero data loss** — all assets extracted and preserved before account shutdown
- ✅ **~5.4 records/second throughput** — scalable estimate for any account size
- ✅ **Fault-tolerant** — pipeline resumes from exact crash point, no re-fetching
- ✅ **Structured output** — flat JSON ready for Excel, database, or platform migration
- ✅ **Subject lines and preheaders** captured for all email assets
- ✅ **HTML content** preserved for full email body migration
- ✅ **Fully automated** — no manual effort required

> **Throughput estimate:** To calculate expected run time for any account size — divide total record count by 5.4 to get approximate seconds.

---

## Next Steps & Reusability

This pipeline was built for a one-time data migration before account shutdown. However the architecture is intentionally designed to be reusable — swapping credentials in `.env` is all that's needed to run it against any SFMC account.

Planned extensions for future client work:

1. **SOAP API Pipeline** — Extract email send tracking data (Job IDs, send stats, bounce rates) via SFMC SOAP API — already in development as a companion pipeline
2. **Target Platform Loader** — Push extracted JSON directly into BigQuery, HubSpot, or Salesforce CRM without rewriting the extraction layer
3. **Email-Only Filter** — Filter assets by `assetType` to isolate email records only
4. **Multi-Account Support** — Pass account credentials dynamically to run across multiple SFMC business units
5. **Incremental Sync** — Adapt checkpoint system to support scheduled incremental pulls instead of one-time full extraction

---

## Setup & Usage

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure `.env`

```env
CLIENT_ID=your_sfmc_client_id
CLIENT_SECRET=your_sfmc_client_secret
SUBDOMAIN=your_sfmc_subdomain
PAGE_SIZE=100
```

### 3. Run

```bash
python main.py
```

### 4. Resume after crash

Just re-run the same command — checkpoint handles the rest automatically:

```bash
python main.py
```

---

## Security

- `.env` file is never committed to version control
- `output/` folder is excluded from version control — contains client data
- SFMC tokens auto-refresh on expiry