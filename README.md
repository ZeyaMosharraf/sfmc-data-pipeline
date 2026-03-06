# SFMC Content Asset Extraction Pipeline
### Digital Marketing Agency | Data Engineering & Migration

---

## Executive Summary

| | |
|---|---|
| **Industry** | Digital Marketing Agency (B2B & Franchise) |
| **Platform** | Salesforce Marketing Cloud (SFMC) |
| **Problem** | No native way to bulk-export Content Builder assets with structured metadata |
| **Solution** | Automated Python pipeline using SFMC REST API to extract, transform and save all assets |
| **Records Extracted** | 4,277 assets |
| **Pages Fetched** | 86 pages |
| **Time to Complete** | ~13 minutes |
| **Duplicates Found** | 0 |
| **Next Step** | CRM Migration Pipeline |

---

## Business Problem

Salesforce Marketing Cloud (SFMC) does not provide a built-in export tool for Content Builder assets. Marketing and operations teams had no efficient way to:

- Audit all email assets (subject lines, preheaders, HTML content) at scale
- Extract structured metadata from thousands of assets
- Migrate content from SFMC to another CRM or platform
- Identify duplicate, outdated or unused assets across the account

This created a bottleneck for any data migration, content auditing, or platform transition project.

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
SFMC API → Authentication → Paginated Fetch → Transform → Checkpoint → JSON Output
```

### Project Structure

```
sfmc-data-pipeline/
├── main.py                  # Entry point — orchestrates fetch, transform, save
├── clients/
│   ├── __init__.py
│   └── sfmc_client.py       # SFMC API client — auth token + POST fetch
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
├── output/
│   └── sfmc_assets.json     # Final output (auto-generated)
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
| **OAuth2 Authentication** | SFMC client credentials token flow |
| **Pagination Handling** | 86 pages × 50 records, with smart stop logic |
| **JSON Transformation** | Nested JSON flattening with dot notation paths |
| **Checkpoint & Resume** | Fault-tolerant pipeline with page + last_id state |
| **Logging** | Structured per-page logging with timestamps |
| **Environment Config** | `.env` based secrets management |

---

## Results & Business Impact

- ✅ **4,277 assets** successfully extracted with zero data loss
- ✅ **Fault-tolerant** — pipeline resumes from exact crash point, no re-fetching
- ✅ **Structured output** — flat JSON ready for Excel, database, or CRM import
- ✅ **Subject lines and preheaders** captured for all email assets
- ✅ **HTML content** available for full email body migration
- ✅ **13 minutes** to extract the full account — fully automated, no manual effort

### Business Recommendation

Any digital marketing agency managing large SFMC accounts should have an automated extraction layer. Manual exports are error-prone, incomplete, and not scalable. This pipeline provides a reliable foundation for:

- Content audits
- Platform migrations
- Asset reporting
- Compliance and archiving

---

## Next Steps

1. **CRM Migration** — Adapt pipeline to push extracted assets directly into a target CRM (e.g. HubSpot, Salesforce CRM)
2. **Excel Export** — Convert JSON output to formatted `.xlsx` for stakeholder reporting
3. **Email-Only Filter** — Filter assets by `assetType` to isolate only email records
4. **HTML Content Extraction** — Parse and store full email HTML separately for content migration
5. **Scheduling** — Add cron job or scheduler to run pipeline incrementally on a regular basis
6. **Multi-Account Support** — Extend to support multiple SFMC business units

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
PAGE_SIZE=50
```

### 3. Run

```bash
python main.py
```

### 4. Resume after crash

Just re-run the same command — checkpoint handles the rest:

```bash
python main.py
```

---

## Security

- `.env` file is never committed to version control
- Add `.env` to `.gitignore`
- SFMC tokens auto-refresh on expiry