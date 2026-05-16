# Performance

## Current Performance Profile

Performance is primarily constrained by SFMC API latency and sequential extraction flow. The current design favors reliability and restart safety over maximal throughput.

## Retry Optimization

Retry behavior uses `urllib3.Retry` with controlled backoff for retryable status codes:

- 429
- 500
- 502
- 503
- 504

Benefits:

- fewer failed runs from temporary platform instability
- improved completion probability without manual intervention

Optimization opportunities:

- jittered backoff
- retry budget by endpoint
- rate-limit-aware dynamic delays

## Session Pooling

A shared `requests.Session` instance is reused across calls, reducing:

- TCP/TLS setup overhead
- connection churn
- request latency variance

This is a core throughput and stability control for both pipelines.

## Incremental Write Strategy

Data is written repeatedly during execution, creating durable checkpoints in output artifacts. This improves recovery posture but introduces rewrite overhead as output grows.

Tradeoff:

- **Reliability gain:** high
- **Write efficiency at scale:** moderate/low (current implementation)

## Payload Minimization Strategy

The pipeline extracts only selected fields configured in `config/sfmc_columns.py`, limiting unnecessary payload processing and reducing transform overhead.

Further minimization options:

- enforce source-side field projection where API allows
- remove non-essential nested payloads for migration-specific runs

## Current Bottlenecks

| Bottleneck | Effect |
|---|---|
| Sequential API loops | limits parallel throughput |
| In-memory accumulation | increases RAM with dataset size |
| Full-file rewrites | increasing I/O cost over time |
| Single worker runtime | no horizontal scaling |

## Future Optimization Opportunities

1. switch to chunked append-friendly storage formats
2. introduce async request model with bounded concurrency
3. partition extraction windows for parallel workers
4. externalize checkpoints for distributed execution
5. write directly to object storage + columnar files
6. add profiling metrics for latency, retries, and batch durations
