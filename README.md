# SFMC Data Extraction Pipeline

Python data extraction project for Salesforce Marketing Cloud (SFMC), with two independent pipelines:

1. **REST pipeline** for Content Builder asset extraction (subject, preheader, HTML content).
2. **SOAP pipeline** for Send tracking extraction (delivery and engagement metrics).

This project is designed for large exports before account decommissioning, with resume support through checkpoint files.

---

## What this project does

### REST pipeline (Content Builder)
- Authenticates with SFMC OAuth2 (client credentials).
- Calls `/asset/v1/content/assets/query` in paginated mode.
- Extracts selected fields into flattened JSON rows.
- Writes incremental output to `output/sfmc_html.json`.
- Saves resume state in `state/rest_checkpoint.json` (`page`, `last_id`).

### SOAP pipeline (Send tracking)
- Reuses OAuth token flow.
- Calls SOAP `Retrieve` on `Send` object.
- Continues batch retrieval via `ContinueRequest` / `RequestID`.
- Writes incremental output to `output/sfmc_soap.json`.
- Saves resume state in `state/soap_checkpoint.json` (`request_id`).

---

## Project structure

```text
sfmc-data-pipeline/
├── main.py
├── clients/
│   ├── sfmc_client.py
│   └── sfmc_soap_client.py
├── config/
│   ├── settings.py
│   └── sfmc_columns.py
├── state/
│   └── checkpoint.py
├── transform/
│   ├── extract.py
│   ├── soap_extract.py
│   └── flatten.py
├── utils/
│   └── logger.py
├── output/
├── requirements.txt
└── README.md
```

---

## Requirements

- Python 3.10+ (recommended)
- SFMC API package with:
  - REST access for Content Builder assets
  - SOAP access for Send object retrieval

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Environment configuration

Create a `.env` file in repository root:

```env
SFMC_CLIENT_ID=your_client_id
SFMC_CLIENT_SECRET=your_client_secret
SFMC_SUBDOMAIN=your_subdomain
PAGE_SIZE=100
```

> `settings.py` expects exactly these variable names.

---

## How to run

This repo currently uses a **manual switch in `main.py`**.

At the bottom of `main.py`, choose one:

```python
if __name__ == "__main__":
    run_fetch_rest_data()   # REST
    # run_fetch_soap_data() # SOAP
```

or

```python
if __name__ == "__main__":
    # run_fetch_rest_data() # REST
    run_fetch_soap_data()   # SOAP
```

Then run:

```bash
python main.py
```

---

## Output files

- `output/sfmc_html.json`: REST extracted asset content data.
- `output/sfmc_soap.json`: SOAP extracted send tracking data.

All writes are incremental per page/batch so long-running jobs are recoverable.

---

## Checkpoint and resume behavior

### REST
- Checkpoint file: `state/rest_checkpoint.json`
- Keys:
  - `page`: next page to fetch
  - `last_id`: last processed asset ID

### SOAP
- Checkpoint file: `state/soap_checkpoint.json`
- Keys:
  - `request_id`: SFMC continue token for next SOAP batch

If the process stops unexpectedly, re-run `python main.py` with the same selected pipeline; it resumes from checkpoint.

---

## Common troubleshooting

### 1. `TypeError: load_checkpoint() missing 1 required positional argument: 'filename'`
Cause: `load_checkpoint()` called without filename.
Fix: always call with explicit file, e.g.:

```python
checkpoint = load_checkpoint("rest_checkpoint.json")
```

### 2. Authentication failures (401/403)
- Check `.env` values.
- Confirm package permissions in SFMC.
- Confirm `SFMC_SUBDOMAIN` is correct.

### 3. Empty or partial output
- Review logs for page/batch status.
- Verify selected pipeline in `main.py`.
- Check checkpoint files and retry.

---

## Security notes

- Never commit `.env`.
- Never commit real client output data.
- Keep `output/` and `state/` excluded from git where applicable.

---

## Suggested next improvements

1. Add CLI argument support (`--pipeline rest|soap`) to avoid editing `main.py` each run.
2. Add optional date filters for incremental exports.
3. Add direct CSV/XLSX export step for both outputs.
4. Add tests for checkpoint and parser behavior.
