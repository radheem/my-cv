---
tagline: "Senior Data & Database Systems Platform Engineer"
---

## Experience

### AiVader GmbH / TU Ilmenau (ICS Group) - Research Engineering Intern (5G & Open RAN)
Germany | 02/2026 - 04/2026
- Built multi-datasource telemetry ingestion pipelines (Telegraf -> InfluxDB/MongoDB) to persistently store and index high-frequency 5G performance counters and KPM metrics.
- Designed a Cassandra Feature Store integrated with an automated data-extraction (ETL) pipeline to feed analytical machine learning workflows.
- Automated zero-touch provisioning of GCP credentials, Grafana Service Accounts, and database datasources on boot to establish immediate operational readiness.
- Tech: InfluxDB, MongoDB, Cassandra, Kafka, Telegraf, PostgreSQL, Python, SQL.

### Al Hilal Invest - Senior Software Engineer
Pakistan | 11/2023 - 03/2024
- Architected and dockerized backend services, leading system design reviews to optimize data persistence and transactional workflows across MySQL and MongoDB.
- Engineered new data-driven features and APIs, establishing robust documentation standards for scalable information management systems.
- Streamlined deployment pipelines and infrastructure provisioning on AWS EC2 and Kubernetes to support high-availability data services.

### Bluefin Exchange - Senior Software Engineer
Pakistan | 06/2021 - 08/2023
- Optimized transactional engine performance and data persistence by integrating PostgreSQL and DynamoDB, directly reducing latency spikes in high-throughput exchange services.
- Designed and implemented comprehensive data analytics and monitoring dashboards using Grafana, Prometheus, and OpenTelemetry to track transactional throughput and Kafka consumer lag.
- Led system design reviews and code architecture for critical database-backed services, mentoring junior engineers on scalable data persistence patterns.

## Education

### Technical University of Ilmenau
Master of Research, Computer Systems and Engineering | 04/2024 - Present

### National University of Computer and Engineering Sciences
Bachelor of Science, Computer Science | 06/2016 - 08/2020

## Projects

### My Notebook (Document RAG) ([portfolio](https://radheem.github.io/my-cv/projects/my-notebook/))
- Built a durable, retryable document-ingestion pipeline with Hatchet (extract → chunk → embed → summarize → index), featuring per-step timeouts and crash-resilient retries.
- Implemented vector search with pgvector (HNSW, cosine) and real-time progress streaming over NATS JetStream + SSE for persistent state tracking.
- Deployed cloud-native on k3d with cert-manager TLS and ExternalDNS, keeping all inference local via dual llama.cpp servers behind an OpenAI-compatible API.

### Information Retrieval System (IRS) - Distributed Systems Platform (Stealth Project) ([portfolio](https://radheem.github.io/my-cv/projects/irs/))
- **Built a best-effort ETL side-channel** into **PostgreSQL (sqlc)**, **Dgraph** (graph database), and **DocumentDB** (NoSQL cold-archive), orchestrated by **Hatchet** with declarative routing.
- **Migrated the platform's session state and messaging** off Dapr to native **NATS JetStream (streaming)** and **NATS KV (session state)**, with direct gRPC connections to optimize transactional latency.
- **Integrated multiple third-party vendors** via an adaptor/anti-corruption contract featuring **CUE-based schema mapping** to enforce structural data integrity across heterogeneous sources.
- **Deployed Go microservices** using **Kubernetes**, **kustomize**, **Skaffold**, and **Cilium**, ensuring robust, isolated routing and high-availability operations.

## Skills

- Languages (spoken): English (fluent), German / Deutsch (A2)
- Databases & Persistence: PostgreSQL (sqlc), MySQL, MongoDB/DocumentDB, Dgraph, DynamoDB, BigQuery, Snowflake
- Data & Analytics: pandas, scikit-learn, Kubeflow Pipelines, KServe, Grafana, VictoriaMetrics
- Programming Languages: Python, SQL, Go, TypeScript, JavaScript, Bash, PHP
- Systems & ETL/Streaming: Kafka, NATS (JetStream + KV), Hatchet, MCP (FastMCP), gRPC, Dapr, OpenTelemetry
- Cloud/Infra & Architecture: Kubernetes, kustomize, Skaffold, Cilium, external-dns, Docker, Helm, Terraform, AWS (EC2, RDS, DynamoDB)
- Web: ReactJS, NodeJS, NestJS, Django
