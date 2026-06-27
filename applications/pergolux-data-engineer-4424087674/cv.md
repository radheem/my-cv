---
tagline: "Data Engineer"
---

## Experience
### Al Hilal Invest — Senior Software Engineer
*Pakistan · 11/2023 – 03/2024*
- Dockerized backend services and refined deployment pipelines to enforce idempotency and streamline failure-state management across MySQL and MongoDB data stores.
- Led system design and code reviews to establish clear data contracts, schema evolution standards, and reliable downstream data flows.
- Developed and documented new services and features, maintaining full version control via Git and AWS infrastructure.

### Bluefin Exchange — Senior Software Engineer
*Pakistan · 06/2021 – 08/2023*
- Maintained release processes and documentation for exchange services, prioritizing Git version control, idempotent deployments, and downstream impact evaluation.
- Reviewed system designs to enforce data contracts, schema evolution practices, and reliable data orchestration across Kafka, PostgreSQL, and DynamoDB.
- Identified architecture improvements to integrate OpenTelemetry and Prometheus for comprehensive data pipeline observability and alerting.

### Seed Labs — Software Engineer
*Pakistan · 06/2020 – 06/2021*
- Analyzed, cleaned, and visualized data to present stakeholder insights, applying Python and SQL for robust data transformation and reproducible workflows.
- Researched and delivered data-driven solutions under mentorship, utilizing Git for version control and systematic failure-state management.
- Dockerized data processing services and integrated MySQL/MongoDB persistence layers for scalable analytics.

## Education
### Technical University of Ilmenau
*Master of Research, Computer Systems and Engineering · 04/2024 – Present*
### National University of Computer and Engineering Sciences
*Bachelor of Science, Computer Science · 06/2016 – 08/2020*

## Projects
- **O-RAN Testbed (Open5GS + RIC + OCUDU gNB)** — Engineered a Kafka-based metrics pub/sub pipeline where Python xApps publish per-UE KPM data to a consumer that fans out messages idempotently to InfluxDB 3, MongoDB, and AIMLFW-compatible sinks, ensuring reliable data ingestion and downstream observability.
- **Second Brain (Document RAG)** — Built a durable, retryable document-ingestion pipeline orchestrated by Hatchet with per-step timeouts and crash-resilient retries, streaming real-time progress over NATS JetStream and indexing embeddings via pgvector for reliable vector search.
- **cv-tailor (LLM CV/Cover Tailoring + LinkedIn Automation)** — Developed a Python-driven automation pipeline with a unit-tested ranker and Git-versioned application tracker, enforcing reproducible generation through manifest tracking and quality-benchmark regression gates while securing data with in-browser encryption.

## Skills
- **Languages** — English (fluent), Deutsch (A2)
- **Programming Languages** — Python, SQL, Go, TypeScript, JavaScript, Bash, PHP
- **Databases & Persistence** — Snowflake, PostgreSQL, MySQL, MongoDB/DocumentDB, Dgraph, DynamoDB, BigQuery, pgvector
- **AI / ML Integration** — MCP, Kubeflow, KServe, scikit-learn, TensorFlow/Keras, pgvector, llama.cpp
- **Observability & Reliability** — OpenTelemetry, VictoriaMetrics, Prometheus, Grafana
