# REST Pipeline

```mermaid
flowchart TD
    A[Start REST Run] --> B[Load rest_checkpoint.json]
    B --> C[Acquire OAuth Token]
    C --> D[POST assets/query page=N]
    D --> E{Items Returned?}
    E -->|No| J[Complete]
    E -->|Yes| F[Transform REST Fields]
    F --> G[Write output/sfmc_html.json]
    G --> H[Save checkpoint page + last_id]
    H --> I{len(items) == pageSize?}
    I -->|Yes| D
    I -->|No| K[Clear checkpoint]
    K --> J
```
