---
tagline: "Senior Data & Database Systems Platform Engineer"
---

## Experience

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

### Seed Labs - Software Engineer
Pakistan | 06/2020 - 06/2021
- Engineered data ETL pipelines and analytical workflows using Python and SQL, cleaning and transforming raw datasets for stakeholder reporting.
- Developed data visualization charts and insights dashboards to communicate analytical findings, leveraging MySQL and MongoDB for persistent data storage.

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

### cv-tailor (LLM CV/Cover Tailoring + LinkedIn Automation) ([portfolio](https://radheem.github.io/my-cv/projects/cv-tailor/))
- Engineered a Python CLI and **FastMCP Server** automating CV/Cover letter tailoring with unit-tested project ranking (Anthropic/Ollama) and hallucination guards.
- Developed an automated **Gmail alert ingestion** pipeline and lightweight guest API fetching, integrated with bi-directional **Google Sheets synchronization** for lifecycle tracking.
- Secured sensitive documents in Git using client-side **AES-256-GCM** encryption, gated behind password-protected static Pages.

## Skills

- Languages (spoken): English (fluent), German / Deutsch (A2)
- Databases & Persistence: PostgreSQL (sqlc), MySQL, MongoDB/DocumentDB, Dgraph, DynamoDB, BigQuery, Snowflake
- Data & Analytics: pandas, scikit-learn, Kubeflow Pipelines, KServe, Grafana, VictoriaMetrics
- Programming Languages: Python, SQL, Go, TypeScript, JavaScript, Bash, PHP
- Systems & ETL/Streaming: Kafka, NATS (JetStream + KV), Hatchet, MCP (FastMCP), gRPC, Dapr, OpenTelemetry
- Cloud/Infra & Architecture: Kubernetes, kustomize, Skaffold, Cilium, external-dns, Docker, Helm, Terraform, AWS (EC2, RDS, DynamoDB)
- Web: ReactJS, NodeJS, NestJS, Django
