---
tagline: "Senior Data & Database Systems Platform Engineer"
---

## Experience

### Al Hilal Invest - Senior Software Engineer
Pakistan | 11/2023 - 03/2024
- Led system design reviews and code reviews, focusing on data persistence layers, transactional integrity, and scalable architecture.
- Improved deployment processes and dockerized backend services, optimizing MySQL and MongoDB data routing and storage efficiency.
- Developed and documented new services and features, implementing data visualization and analytics dashboards for stakeholder reporting.
- Tech: NodeJS, PHP, TypeScript, ReactJS, Docker, MySQL, MongoDB, AWS S3, AWS EC2, Kubernetes.

### Bluefin Exchange - Senior Software Engineer
Pakistan | 06/2021 - 08/2023
- Integrated Prometheus logging, OpenTelemetry metrics, and Grafana alerts to monitor transaction engine throughput and Kafka consumer group lag, reducing latency spikes and enabling real-time analytics.
- Identified system design improvements and proposed solutions independently, focusing on PostgreSQL persistence, DynamoDB data modeling, and high-availability architecture.
- Reviewed code and design decisions as a system expert for select services, ensuring robust ETL pipelines, data consistency, and query optimization.
- Maintained release processes and documentation for a set of exchange services.
- Led teams of junior engineers on project initiatives.
- Tech: ReactJS, NodeJS, Go, Python, TypeScript, Docker, PostgreSQL, DynamoDB, Kafka, Terraform, Kubernetes, Prometheus, Grafana, OpenTelemetry.

### Seed Labs - Software Engineer
Pakistan | 06/2020 - 06/2021
- Analyzed, cleaned, and visualized data to present insights to stakeholders, building custom charts and analytics reports for business intelligence.
- Researched solutions and proposed designs for implementation, focusing on MySQL and MongoDB data architecture and schema design.
- Delivered solutions in teams of three under mentorship of senior engineers, implementing Python-based data processing and transformation pipelines.
- Tech: Python, scikit-learn, NodeJS, TensorFlow, Docker, MongoDB, MySQL, AWS EC2.

## Education

### Technical University of Ilmenau
Master of Research, Computer Systems and Engineering | 04/2024 - Present

### National University of Computer and Engineering Sciences
Bachelor of Science, Computer Science | 06/2016 - 08/2020

## Projects

### Second Brain (Document RAG)
Self-hosted RAG document-intelligence service: durable Hatchet ingestion, local llama.cpp inference, pgvector semantic search, NATS JetStream progress streaming on a k3d homelab.
- Built a durable, retryable document-ingestion pipeline with Hatchet (extract → chunk → embed → summarize → index) with per-step timeouts and retries, instrumented with OpenTelemetry and custom Grafana dashboards.
- Designed real-time progress streaming over NATS JetStream + SSE (durable stream + KV current-state).
- Kept all inference local and private via two llama.cpp servers (chat + embeddings) behind an OpenAI-compatible API.
- Implemented vector search with pgvector (HNSW, cosine); deployed cloud-native on k3d with cert-manager TLS and ExternalDNS.

### cv-tailor (LLM CV/Cover Tailoring + LinkedIn Automation)
Python CLI tool and FastMCP server that turns a job posting into a tailored CV + cover letter: pure ranker picks facts and LLM only writes prose, with automated multi-source Gmail alert ingestion (LinkedIn, Indeed, Glassdoor, Fraunhofer), and Google Sheets lifecycle syncing.
- Built a Python CLI and FastMCP Server that automates CV/Cover letter tailoring using unit-tested project ranking (Anthropic/Ollama) and guards against hallucinations.
- Developed an automated Gmail alert ingestion pipeline (LinkedIn, Glassdoor, Indeed, Fraunhofer) and lightweight guest API fetching.
- Integrated a bi-directional Google Sheets synchronization using Google Apps Script to track job application lifecycles.
- Secured documents in Git using client-side AES-256-GCM encryption gated on password-protected static Pages.

### Information Retrieval System (IRS)
Distributed Systems Platform (Stealth Project)
- Built Go microservices with gRPC and gRPC-Gateway using Protobuf-first APIs and Buf tooling.
- Migrated the platform off Dapr to native NATS JetStream (messaging), NATS KV (session state), and direct gRPC.
- Built an MCP (Model Context Protocol) integration exposing the platform to LLM agents as declarative, hot-reloadable tools via a config-driven toolbox server.
- Built a per-user authenticated browser-session service (Playwright) with gateway consistent-hashing and an AES-256-GCM credential vault.
- Built a best-effort ETL side-channel into PostgreSQL (sqlc), Dgraph, and DocumentDB, orchestrated by Hatchet with declarative routing; verified by a Ginkgo E2E gate.
- Integrated multiple bot-protected third-party vendors via an adaptor/anti-corruption contract with CUE-based schema mapping.
- Deployed with Kubernetes, kustomize, Skaffold, Cilium, and external-dns; integrated OpenTelemetry distributed tracing and Prometheus metric collection across all Go microservices.

## Skills

- Languages (spoken): English (fluent), German / Deutsch (A2)
- Databases: PostgreSQL (sqlc), MySQL, MongoDB/DocumentDB, Dgraph, DynamoDB, BigQuery, Snowflake
- Systems: gRPC, NATS (JetStream + KV), Hatchet, MCP (FastMCP), Kafka, Dapr, OpenTelemetry, VictoriaMetrics, Grafana
- ML/Data: Kubeflow Pipelines, KServe, scikit-learn, TensorFlow/Keras, pandas
- Cloud/Infra: Kubernetes, kustomize, Skaffold, Cilium, external-dns, Docker, Helm, Terraform, AWS (EC2, RDS, DynamoDB)
- Programming Languages: Go, Python, SQL, TypeScript, JavaScript, Bash, PHP
- Web: ReactJS, NodeJS, NestJS, Django
