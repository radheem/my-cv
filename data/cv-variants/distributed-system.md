---
tagline: "Senior Backend & Distributed Systems Engineer"
---

## Experience

### Al Hilal Invest - Senior Software Engineer
Pakistan | 11/2023 - 03/2024
- Led system design reviews and architectural decisions for backend services, ensuring scalable microservice boundaries and clean API contracts.
- Improved deployment pipelines and containerized backend services using Docker, enabling consistent environments across AWS EC2 and Kubernetes.
- Developed and documented new services and features across NodeJS, TypeScript, and PHP stacks, integrating with MySQL and MongoDB data stores.
- Tech: NodeJS, PHP, TypeScript, ReactJS, Docker, MySQL, MongoDB, AWS S3, AWS EC2, Kubernetes.

### Bluefin Exchange - Senior Software Engineer
Pakistan | 06/2021 - 08/2023
- Identified and implemented system design improvements to optimize transaction engine throughput, leveraging Go, NodeJS, and Python microservices.
- Integrated Prometheus logging, OpenTelemetry metrics, and Grafana alerts to monitor Kafka consumer group lag and reduce latency spikes across distributed services.
- Reviewed code and architectural decisions as a system expert, enforcing best practices for backend APIs and event-driven messaging patterns.
- Maintained release processes and technical documentation for core exchange services, while leading junior engineering teams on project initiatives.
- Tech: ReactJS, NodeJS, Go, Python, TypeScript, Docker, PostgreSQL, DynamoDB, Kafka, Terraform, Kubernetes, Prometheus, Grafana, OpenTelemetry.

### Seed Labs - Software Engineer
Pakistan | 06/2020 - 06/2021
- Researched architectural solutions and proposed system designs for implementation, focusing on scalable backend and data processing pipelines.
- Delivered full-stack and backend solutions in collaborative teams under senior mentorship, utilizing Python, NodeJS, and TensorFlow.
- Analyzed, cleaned, and visualized complex datasets to present actionable insights to stakeholders, supporting data-driven decision making.
- Tech: Python, scikit-learn, NodeJS, TensorFlow, Docker, MongoDB, MySQL, AWS EC2.

## Education

### Technical University of Ilmenau
Master of Research, Computer Systems and Engineering | 04/2024 - Present

### National University of Computer and Engineering Sciences
Bachelor of Science, Computer Science | 06/2016 - 08/2020

## Projects

### Information Retrieval System (IRS) - Distributed Systems Platform
- Engineered a suite of Go microservices with gRPC and gRPC-Gateway, utilizing Protobuf-first APIs and Buf tooling for strict contract-driven communication.
- Migrated the platform from Dapr to native NATS JetStream for event-driven messaging and NATS KV for distributed session state, alongside direct gRPC calls.
- Developed an MCP (Model Context Protocol) integration exposing the platform to LLM agents as declarative, hot-reloadable tools via a config-driven toolbox server.
- Built a per-user authenticated browser-session service with gateway consistent-hashing and an AES-256-GCM credential vault, deployed on Kubernetes with Cilium networking and OpenTelemetry distributed tracing.
- Implemented a best-effort ETL side-channel into PostgreSQL, Dgraph, and DocumentDB orchestrated by Hatchet with declarative routing, verified by Ginkgo E2E gates.

### Second Brain - Self-Hosted Document RAG
- Architected a durable, retryable document-ingestion pipeline using Hatchet (extract → chunk → embed → summarize → index) with per-step timeouts, instrumented with OpenTelemetry and custom Grafana dashboards.
- Designed real-time progress streaming over NATS JetStream + SSE, leveraging durable streams and KV stores for current-state synchronization.
- Maintained all inference locally and privately via two llama.cpp servers (chat + embeddings) behind an OpenAI-compatible API, deployed on k3d with cert-manager TLS and ExternalDNS.
- Implemented high-performance vector search with pgvector (HNSW, cosine) for semantic retrieval within the document intelligence service.

### cv-tailor - LLM CV/Cover-Letter Tailoring + LinkedIn Automation
- Built a Python CLI and FastMCP Server that automates CV/Cover letter tailoring using unit-tested project ranking (Anthropic/Ollama) and guards against hallucinations.
- Developed an automated Gmail alert ingestion pipeline (LinkedIn, Glassdoor, Indeed, Fraunhofer) and lightweight guest API fetching for job market data.
- Integrated a bi-directional Google Sheets synchronization using Google Apps Script to track job application lifecycles and maintain state consistency.
- Secured sensitive documents in Git using client-side AES-256-GCM encryption gated on password-protected static Pages, ensuring privacy in a fullstack automation workflow.

## Skills

- Languages (spoken): English (fluent), German / Deutsch (A2)
- Systems & Messaging: gRPC, NATS (JetStream + KV), Hatchet, MCP (FastMCP), Kafka, Dapr, OpenTelemetry, VictoriaMetrics, Grafana
- Cloud & Infrastructure: Kubernetes, kustomize, Skaffold, Cilium, external-dns, Docker, Helm, Terraform, AWS (EC2, RDS, DynamoDB)
- Programming Languages: Go, Python, SQL, TypeScript, JavaScript, Bash, PHP
- Databases: PostgreSQL (sqlc), MySQL, MongoDB/DocumentDB, Dgraph, DynamoDB, BigQuery, Snowflake
- Web & Fullstack: ReactJS, NodeJS, NestJS, Django
- ML & Data: Kubeflow Pipelines, KServe, scikit-learn, TensorFlow/Keras, pandas
