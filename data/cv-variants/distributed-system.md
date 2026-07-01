---
tagline: "Senior Backend & Distributed Systems Engineer"
---

## Experience

### Al Hilal Invest - Senior Software Engineer
Pakistan | 11/2023 - 03/2024
- Architected and documented scalable backend services and fullstack features, leveraging NodeJS, TypeScript, and ReactJS to deliver robust API-driven solutions.
- Led system design reviews and API architecture decisions to ensure robust microservice boundaries, distributed system reliability, and clean separation of concerns.
- Containerized backend services with Docker and optimized deployment pipelines on AWS EC2/S3 and Kubernetes, improving release velocity and infrastructure consistency.
- Tech: NodeJS, PHP, TypeScript, ReactJS, Docker, MySQL, MongoDB, AWS S3, AWS EC2, Kubernetes.

### Bluefin Exchange - Senior Software Engineer
Pakistan | 06/2021 - 08/2023
- Engineered high-throughput distributed systems and event-driven messaging pipelines using Go, NodeJS, and Kafka, directly reducing latency spikes through optimized consumer group management.
- Integrated Prometheus logging, OpenTelemetry metrics, and Grafana alerts to monitor transaction engine throughput and Kafka consumer group lag, establishing comprehensive observability for backend services.
- Served as system design authority for core exchange services, conducting rigorous code reviews and proposing architectural improvements for scalability, fault tolerance, and fullstack integration.
- Managed release lifecycles and technical documentation while mentoring junior engineers on distributed backend patterns, API design, and cloud-native deployment practices.
- Tech: ReactJS, NodeJS, Go, Python, TypeScript, Docker, PostgreSQL, DynamoDB, Kafka, Terraform, Kubernetes, Prometheus, Grafana, OpenTelemetry.

### Seed Labs - Software Engineer
Pakistan | 06/2020 - 06/2021
- Designed and delivered backend data pipelines and fullstack solutions in cross-functional teams, utilizing Python, NodeJS, and containerized deployments under senior mentorship.
- Researched and proposed scalable system designs, focusing on efficient data processing, API-driven backend integration, and architectural best practices.
- Analyzed, cleaned, and visualized complex datasets to transform raw inputs into actionable insights, presenting technical findings to stakeholders.
- Tech: Python, scikit-learn, NodeJS, TensorFlow, Docker, MongoDB, MySQL, AWS EC2.

## Education

### Technical University of Ilmenau
Master of Research, Computer Systems and Engineering | 04/2024 - Present

### National University of Computer and Engineering Sciences
Bachelor of Science, Computer Science | 06/2016 - 08/2020

## Projects

### Second Brain (Document RAG)
- Built a durable, retryable document-ingestion pipeline with Hatchet (extract → chunk → embed → summarize → index) with per-step timeouts and retries, instrumented with OpenTelemetry and custom Grafana dashboards.
- Designed real-time progress streaming over NATS JetStream + SSE (durable stream + KV current-state).
- Kept all inference local and private via two llama.cpp servers (chat + embeddings) behind an OpenAI-compatible API.
- Implemented vector search with pgvector (HNSW, cosine); deployed cloud-native on k3d with cert-manager TLS and ExternalDNS.
- [repo](https://github.com/radheem/my-notebook)

### cv-tailor (LLM CV/Cover Tailoring + LinkedIn Automation)
- Built a Python CLI and FastMCP Server that automates CV/Cover letter tailoring using unit-tested project ranking (Anthropic/Ollama) and guards against hallucinations.
- Developed an automated Gmail alert ingestion pipeline (LinkedIn, Glassdoor, Indeed, Fraunhofer) and lightweight guest API fetching.
- Integrated a bi-directional Google Sheets synchronization using Google Apps Script to track job application lifecycles.
- Secured documents in Git using client-side AES-256-GCM encryption gated on password-protected static Pages.
- [repo](https://github.com/radheem/cv-tailor)

### Information Retrieval System (IRS)
- Built Go microservices with gRPC and gRPC-Gateway using Protobuf-first APIs and Buf tooling.
- Migrated the platform off Dapr to native NATS JetStream (messaging), NATS KV (session state), and direct gRPC.
- Built an MCP (Model Context Protocol) integration exposing the platform to LLM agents as declarative, hot-reloadable tools via a config-driven toolbox server.
- Built a per-user authenticated browser-session service (Playwright) with gateway consistent-hashing and an AES-256-GCM credential vault.
- Built a best-effort ETL side-channel into PostgreSQL (sqlc), Dgraph, and DocumentDB, orchestrated by Hatchet with declarative routing; verified by a Ginkgo E2E gate.
- Integrated multiple bot-protected third-party vendors via an adaptor/anti-corruption contract with CUE-based schema mapping.
- Deployed with Kubernetes, kustomize, Skaffold, Cilium, and external-dns; integrated OpenTelemetry distributed tracing and Prometheus metric collection across all Go microservices.

## Skills

- Languages (spoken): English (fluent), German / Deutsch (A2)
- Systems & Messaging: gRPC, NATS (JetStream + KV), Hatchet, MCP (FastMCP), Kafka, Dapr, OpenTelemetry, VictoriaMetrics, Grafana
- Programming Languages: Go, Python, SQL, TypeScript, JavaScript, Bash, PHP
- Web & Fullstack: ReactJS, NodeJS, NestJS, Django
- Databases & Storage: PostgreSQL (sqlc), MySQL, MongoDB/DocumentDB, Dgraph, DynamoDB, BigQuery, Snowflake
- Cloud & Infrastructure: Kubernetes, kustomize, Skaffold, Cilium, external-dns, Docker, Helm, Terraform, AWS (EC2, RDS, DynamoDB)
- ML & Data Processing: Kubeflow Pipelines, KServe, scikit-learn, TensorFlow/Keras, pandas
