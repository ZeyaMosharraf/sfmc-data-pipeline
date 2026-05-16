# Engineering Decisions

## Decision 1: Dual-Pipeline Architecture

**Decision**  
Use two extraction pipelines under one orchestration layer.

**Context**  
SFMC exposes required migration data across REST and SOAP surfaces.

**Problem**  
A single generalized extractor would hide protocol differences and increase complexity.

**Chosen Approach**  
Maintain dedicated REST and SOAP clients with shared cross-cutting infrastructure.

**Tradeoffs**  
- **Pros:** clarity, protocol correctness, easier incident isolation  
- **Cons:** additional modules and separate flow logic

**Future Improvements**  
Introduce shared orchestration interfaces while keeping protocol-specific implementations.

---

## Decision 2: REST/SOAP Isolation

**Decision**  
Keep transport payload construction and parsing isolated by protocol.

**Context**  
REST uses JSON + page semantics; SOAP uses XML + continuation token semantics.

**Problem**  
Cross-protocol abstractions become leaky and error-prone.

**Chosen Approach**  
Implement isolated clients (`sfmc_client.py`, `sfmc_soap_client.py`) and isolated transforms.

**Tradeoffs**  
- **Pros:** maintainability, lower defect risk  
- **Cons:** less code sharing in extraction/parsing layers

**Future Improvements**  
Standardize internal event contracts after parsing for downstream uniformity.

---

## Decision 3: Incremental Writes

**Decision**  
Persist outputs incrementally during extraction loops.

**Context**  
Long-running jobs are vulnerable to interruption.

**Problem**  
End-of-run write only would risk total progress loss.

**Chosen Approach**  
Append transformed rows in-memory and rewrite durable JSON output per loop iteration.

**Tradeoffs**  
- **Pros:** durable progress, recoverability  
- **Cons:** repeated file writes and growing rewrite cost

**Future Improvements**  
Move to append-only newline-delimited JSON, parquet micro-batches, or object-store multipart writes.

---

## Decision 4: Checkpoint Persistence

**Decision**  
Persist continuation state in local checkpoint files.

**Context**  
Extraction needs exact resume points for both pipelines.

**Problem**  
Without state persistence, retries require full reruns.

**Chosen Approach**  
Store protocol-specific checkpoint metadata in `state/`.

**Tradeoffs**  
- **Pros:** fast restart, simple implementation  
- **Cons:** local-disk dependency; no multi-worker coordination

**Future Improvements**  
External checkpoint store (Redis/Postgres/object metadata) with optimistic locking.

---

## Decision 5: Centralized Schema Mapping

**Decision**  
Centralize selected source fields in `config/sfmc_columns.py`.

**Context**  
Field shape changes should not require edits across multiple files.

**Problem**  
Scattered field lists cause drift and brittle maintenance.

**Chosen Approach**  
Use centralized property lists consumed by transforms and SOAP parser.

**Tradeoffs**  
- **Pros:** single source of truth, consistent projection  
- **Cons:** manual update path for schema evolution

**Future Improvements**  
Introduce schema registry and automated compatibility checks.

---

## Decision 6: Retries + Session Reuse

**Decision**  
Use one shared `requests.Session` with retry policy and backoff.

**Context**  
SFMC APIs can return transient 429/5xx failures.

**Problem**  
Naive request flow causes avoidable failures and connection overhead.

**Chosen Approach**  
Session pooling + `urllib3.Retry` for retryable status codes.

**Tradeoffs**  
- **Pros:** better throughput stability, fewer transient failures  
- **Cons:** requires careful tuning to avoid retry storms

**Future Improvements**  
Adaptive retry based on response headers and dynamic rate-limit budget management.

---

## Decision 7: Transform Layer Separation

**Decision**  
Separate extraction/transformation from API request code.

**Context**  
Transformation logic evolves independently of transport behavior.

**Problem**  
Mixing transform and IO logic reduces testability and readability.

**Chosen Approach**  
Dedicated transform modules (`extract.py`, `soap_extract.py`) with pure row normalization behavior.

**Tradeoffs**  
- **Pros:** cleaner boundaries, easier unit testing  
- **Cons:** additional module interfaces to maintain

**Future Improvements**  
Add schema validation, type contracts, and standardized data quality checks in transform stage.
