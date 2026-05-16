# Scalability

## Current Scalability Characteristics

| Dimension | Current State | Implication |
|---|---|---|
| Execution model | Single process | Simple operations, limited parallel throughput |
| API concurrency | Sequential paging/batching | Stable ordering, lower extraction rate ceiling |
| State management | Local file checkpoints | Strong single-run recovery, not distributed-safe |
| Output persistence | Rewritten JSON artifacts | Reliable local durability, increasing write overhead |

## Bottlenecks

1. **Network/API latency** to SFMC endpoints.
2. **Sequential control flow** in both pipelines.
3. **Output rewrite cost** as payload size grows.
4. **In-process memory accumulation** for full result lists.

## Memory Considerations

- Current implementation keeps accumulated rows in memory before each rewrite.
- Memory usage increases linearly with extracted dataset volume.
- At higher record counts, this can become the primary runtime limiter.

Recommended near-term improvement:

- stream writes in chunked batches (NDJSON/Parquet) and avoid holding full datasets in memory.

## Retry Scalability

Retry behavior is centralized and protects against transient faults, but scaling retries requires:

- jittered backoff to avoid synchronized spikes
- per-endpoint retry budgets
- explicit handling for prolonged throttling windows

## Partitioning Strategies

Potential partition keys for horizontal scaling:

- REST: asset id ranges, modified date windows, business unit partitions
- SOAP: date windows, account-level partitioning, send-id ranges

Partition controls should preserve idempotency and deterministic merge behavior downstream.

## Future Scaling Roadmap

### 1. Distributed Processing

- worker pool per partition
- distributed checkpoint/state backend
- centralized orchestration and lease-based work claiming

### 2. Async Processing

- async HTTP clients for high-latency endpoints
- controlled concurrency windows per API domain
- backpressure-aware queueing

### 3. Storage/Compute Decoupling

- direct writes to object storage (ADLS/S3/GCS)
- batch landing zones with versioned partitions
- downstream warehouse ingestion (Snowflake/BigQuery/Synapse/Databricks SQL)

## Warehouse and Object Storage Integration Roadmap

| Target | Why It Matters | Scaling Benefit |
|---|---|---|
| Object storage landing zone | Durable, cheap, large-scale retention | Enables replay, partition pruning, lifecycle policies |
| Columnar formats (Parquet) | Efficient analytics reads | Reduced scan and compute cost |
| Warehouse external tables | Queryability and BI access | Operational and analytical consumption at scale |
| Metadata-driven ingestion | Controlled schema evolution | Safer multi-source growth |

## Target End State

A partitioned, asynchronous, checkpoint-distributed extraction platform that writes durable, analytics-ready datasets into object storage and warehouses, while preserving protocol-specific extraction correctness.
