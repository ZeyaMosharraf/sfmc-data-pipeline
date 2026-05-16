# Roadmap

## Engineering Roadmap

This roadmap prioritizes production hardening, scale readiness, and operational visibility.

## Platform Evolution Themes

| Initiative | Why It Matters | Engineering Maturity Impact | Business Value |
|---|---|---|---|
| Airflow orchestration | Scheduled, managed DAG execution | Moves from script-run to orchestrated platform | Predictable operations and lower manual effort |
| Async extraction | Better use of IO wait time | Increases throughput sophistication | Faster migration completion windows |
| Distributed checkpointing | Multi-worker fault tolerance | Enables horizontally scalable execution | Higher reliability for large exports |
| Cloud deployment | Standardized runtime environments | Improves repeatability and infra hygiene | Faster onboarding and lower ops risk |
| CI/CD | Controlled promotion and release quality | Introduces disciplined delivery | Fewer regressions and safer changes |
| Observability | Deep runtime and incident insight | Operational excellence baseline | Faster issue resolution |
| Structured logging | Machine-parseable telemetry | Improves traceability and automation | Better auditability/compliance support |
| Metrics collection | Quantifiable performance and reliability | SLO-oriented operations | Capacity planning and SLA confidence |
| Dead-letter queues | Isolate non-recoverable records | Advanced failure handling maturity | Prevents pipeline-wide stoppage |
| Warehouse integration | Query-ready analytical destination | Completes data platform integration | Accelerates reporting and analytics |
| Object storage landing | Durable, scalable data lake ingest | Foundation for large-scale data management | Lower storage cost and long-term retention |
| Schema validation | Contract enforcement at ingest | Improves data quality governance | Reduces downstream breakage |
| Containerization | Portable and reproducible runtime | Standardized deployment artifact | Consistent execution across environments |

## Planned Milestones

### Milestone 1: Operational Foundation

- containerized runtime
- CI/CD pipeline with lint/test/build gates
- structured logs and baseline metrics

### Milestone 2: Reliability Expansion

- orchestrated schedules with Airflow
- dead-letter handling for persistent bad records
- schema validation layer before persistence

### Milestone 3: Scale-Out Architecture

- async extraction for high-latency endpoints
- partitioned workload execution
- distributed checkpoint backend

### Milestone 4: Data Platform Integration

- object storage landing zone
- warehouse load patterns and table contracts
- automated reconciliation and quality dashboards

## Target End State

A cloud-deployed, observable, orchestrated extraction platform capable of distributed, restart-safe SFMC migration at enterprise scale with governed data contracts and analytics-ready outputs.
