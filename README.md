# SFMC Data Extraction Pipeline
### API Data Extraction Pipeline | Python ETL & System Integration

---

## Executive Summary

| | |
|---|---|
| **Type** | Data Engineering & API Integration |
| **Platform** | Salesforce Marketing Cloud (SFMC) |
| **Problem** | Client shutting down SFMC account — all historical data at risk of permanent loss |
| **Solution** | Two automated Python pipelines extracting Content Builder assets (REST) and email send tracking data (SOAP) before shutdown |
| **REST Throughput** | ~5.4 records/second |
| **SOAP Throughput** | ~146 records/second |
| **Output** | Structured JSON + Excel ready for migration or archiving |

---

## Business Problem

The client made the decision to shut down their Salesforce Marketing Cloud account. This created an immediate risk of permanent data loss — years of email content assets and historical send tracking data would become inaccessible once the account was closed.

The challenge was that SFMC does not provide a native bulk export tool for either Content Builder assets or email send tracking data. There was no built-in way to:

- Extract all content assets with structured metadata at scale
- Preserve email content (subject lines, preheaders, HTML) before account closure
- Extract complete email send history (Job IDs, send stats, bounce rates, open rates) via SOAP API
- Produce a clean, structured output ready for archiving or migration to another platform

Manual export was not a viable option given the volume of assets and the time constraint of the account shutdown deadline. An automated extraction pipeline was the only reliable solution.

---

## Solution & Methodology

Built two fully automated Python data pipelines sharing a common architecture:

**Pipeline 1 — Content Builder Assets (REST API):**
1. **Authenticates** with SFMC using OAuth2 client credentials flow
2. **Fetches** all assets page by page via the POST query endpoint (`/asset/v1/content/assets/query`)
3. **Transforms** raw nested JSON into flat structured rows
4. **Saves** output incrementally to JSON after each page
5. **Checkpoints** progress using universal checkpoint system — resumes automatically if interrupted

**Pipeline 2 — Email Send Tracking (SOAP API):**
1. **Authenticates** using the same OAuth2 token reused from Pipeline 1
2. **Fetches** all send records in batches via SOAP `Send` object
3. **Transforms** raw XML response into clean flat dicts
4. **Saves** output incrementally to JSON after each batch
5. **Checkpoints** progress using `RequestID` — resumes automatically if interrupted

### Pipeline Flow

```
REST:  SFMC REST API → Auth → Paginated Fetch → Transform → Checkpoint → JSON → Excel
SOAP:  SFMC SOAP API → Auth → Batch Fetch (ContinueRequest) → Transform → Checkpoint → JSON → Excel
```

### Project Structure

```
sfmc-data-pipeline/
├── main.py                  # Entry point — run_fetch_rest_data() + run_fetch_soap_data()
├── clients/
│   ├── __init__.py
│   ├── sfmc_client.py       # REST — Content Builder assets (OAuth2 + POST query)
│   └── sfmc_soap_client.py  # SOAP — Email send tracking (XML request builder + parser)
├── config/
│   ├── __init__.py
│   ├── settings.py          # Loads environment variables
│   └── sfmc_columns.py      # Defines fields to extract for both pipelines
├── state/
│   ├── __init__.py
│   └── checkpoint.py        # Universal checkpoint — supports any pipeline via filename + dict
├── transform/
│   ├── __init__.py
│   ├── extract.py           # REST — transforms raw JSON items into flat rows
│   ├── soap_extract.py      # SOAP — cleans and flattens XML response rows
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
| **SOAP API Integration** | SFMC Email Send Tracking via XML `Send` object |
| **OAuth2 Authentication** | SFMC client credentials token flow — reused across both pipelines |
| **Pagination Handling** | REST: smart stop via total count — SOAP: ContinueRequest with RequestID |
| **XML Parsing** | `xml.etree.ElementTree` with namespace handling |
| **JSON Transformation** | Nested JSON flattening with dot notation paths |
| **Universal Checkpoint** | Filename + dict pattern — supports REST (page + last_id) and SOAP (request_id) |
| **Logging** | Structured per-batch logging with timestamps and throughput metrics |
| **Environment Config** | `.env` based secrets management |

---

## Results & Business Impact

- ✅ **Zero data loss** — all assets and send history extracted before account shutdown
- ✅ **REST pipeline: ~5.4 records/second** — Content Builder assets
- ✅ **SOAP pipeline: ~146 records/second** — Email send tracking data
- ✅ **Fault-tolerant** — both pipelines resume from exact crash point automatically
- ✅ **Structured output** — flat JSON ready for Excel, database, or platform migration
- ✅ **Subject lines, preheaders and HTML** captured for all email assets
- ✅ **Full send history** preserved — Job IDs, send stats, bounces, opens, clicks
- ✅ **Fully automated** — no manual effort required

> **Throughput estimate:** REST — divide total record count by 5.4 to get approximate seconds. SOAP — divide by 146.

---

## Next Steps & Reusability

This pipeline was built for a one-time data migration before account shutdown. However the architecture is intentionally designed to be reusable — swapping credentials in `.env` is all that's needed to run it against any SFMC account.

Planned extensions for future client work:

1. **Target Platform Loader** — Push extracted JSON directly into BigQuery, HubSpot, or Salesforce CRM without rewriting the extraction layer
2. **Email-Only Filter** — Filter assets by `assetType` to isolate email records only
3. **Multi-Account Support** — Pass account credentials dynamically to run across multiple SFMC business units
4. **Incremental Sync** — Adapt checkpoint system to support scheduled incremental pulls instead of one-time full extraction

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