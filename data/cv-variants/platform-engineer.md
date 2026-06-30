---
tagline: "Senior Cloud Platform & Observability Engineer"
---

## Experience

### Al Hilal Invest - Senior Software Engineer
Pakistan | 11/2023 - 03/2024
- Orchestrated cloud-native deployments and improved CI/CD pipelines by dockerizing backend services and leveraging Kubernetes on AWS EC2/S3 infrastructure.
- Led system design and code reviews, establishing architectural standards for scalable platform services and deployment processes.
- Developed and documented new platform features and integrations across NodeJS, PHP, TypeScript, and ReactJS stacks.
- Tech: Kubernetes, Docker, AWS (EC2, S3), MySQL, MongoDB, NodeJS, PHP, TypeScript, ReactJS

### Bluefin Exchange - Senior Software Engineer
Pakistan | 06/2021 - 08/2023
- Engineered observability and SRE practices by integrating Prometheus logging, OpenTelemetry metrics, and Grafana alerts to monitor transaction engine throughput and Kafka consumer group lag, directly reducing latency spikes.
- Maintained and automated release processes for core exchange services using Terraform and Kubernetes, ensuring platform reliability and consistent deployments.
- Identified and implemented system design improvements, reviewing code and architecture as a technical lead for select platform services.
- Led engineering teams on platform initiatives, mentoring junior engineers on distributed systems, cloud-native best practices, and DevOps workflows.
- Tech: Kubernetes, Terraform, Docker, Prometheus, Grafana, OpenTelemetry, Kafka, Go, Python, NodeJS, PostgreSQL, DynamoDB, TypeScript, ReactJS

### Seed Labs - Software Engineer
Pakistan | 06/2020 - 06/2021
- Containerized and deployed data processing services using Docker on AWS EC2, establishing foundational cloud infrastructure and DevOps practices.
- Researched and proposed system designs for data pipelines, delivering solutions under senior engineering mentorship.
- Analyzed, cleaned, and visualized large-scale datasets to drive platform insights and stakeholder reporting.
- Tech: Docker, AWS EC2, Python, NodeJS, MongoDB, MySQL, scikit-learn, TensorFlow

## Education

### Technical University of Ilmenau
Master of Research, Computer Systems and Engineering | 04/2024 - Present

### National University of Computer and Engineering Sciences
Bachelor of Science, Computer Science | 06/2016 - 08/2020

## Projects

### cv-tailor - LLM CV/Cover-Letter Tailoring + LinkedIn Automation
- Built a Python CLI and **FastMCP Server** that automates CV/Cover letter tailoring using unit-tested project ranking (Anthropic/Ollama) and guards against hallucinations.
- Developed an automated **Gmail alert ingestion** pipeline (LinkedIn, Glassdoor, Indeed, Fraunhofer) and lightweight guest API fetching.
- Integrated a bi-directional **Google Sheets synchronization** using Google Apps Script to track job application lifecycles.
- Secured documents in Git using client-side **AES-256-GCM** encryption gated on password-protected static Pages.

### Second Brain - Self-Hosted Document RAG
- Built a durable, retryable document-ingestion pipeline with Hatchet (extract → chunk → embed → summarize → index) with per-step timeouts and retries, instrumented with OpenTelemetry and custom Grafana dashboards.
- Designed real-time progress streaming over NATS JetStream + SSE (durable stream + KV current-state).
- Kept all inference local and private via two llama.cpp servers (chat + embeddings) behind an OpenAI-compatible API.
- Implemented vector search with pgvector (HNSW, cosine); deployed cloud-native on k3d with cert-manager TLS and ExternalDNS.

### Information Retrieval System (IRS) - Distributed Systems Platform
- Deployed with Kubernetes, kustomize, Skaffold, Cilium, and external-dns; integrated OpenTelemetry distributed tracing and Prometheus metric collection across all Go microservices.
- Migrated the platform off Dapr to native NATS JetStream (messaging), NATS KV (session state), and direct gRPC.
- Built an MCP (Model Context Protocol) integration exposing the platform to LLM agents as declarative, hot-reloadable tools via a config-driven toolbox server.
- Built a per-user authenticated browser-session service (Playwright) with gateway consistent-hashing and an AES-256-GCM credential vault.
- Built a best-effort ETL side-channel into PostgreSQL (sqlc), Dgraph, and DocumentDB, orchestrated by Hatchet with declarative routing; verified by a Ginkgo E2E gate.
- Integrated multiple bot-protected third-party vendors via an adaptor/anti-corruption contract with CUE-based schema mapping.

## Skills

- Languages (spoken): English (fluent), Deutsch (A2)
- Cloud & Platform: Kubernetes, Cilium, Helm, Docker, kustomize, Skaffold, Terraform, AWS (EC2, RDS, DynamoDB, S3), external-dns, k3d, GitOps, DevOps, SRE
- Observability & Reliability: OpenTelemetry, Prometheus, Grafana, VictoriaMetrics, distributed tracing, metrics collection, alerting, platform reliability, latency optimization
- Networking & Messaging: NATS (JetStream + KV), Kafka, gRPC, ZeroMQ, Multus CNI, macvlan, GTP tunneling, policy-based routing, DNS management
- Databases & Storage: PostgreSQL (sqlc), MySQL, MongoDB/DocumentDB, Dgraph, DynamoDB, BigQuery, Snowflake, MinIO/LeoFS
- Programming & Frameworks: Go, Python, SQL, TypeScript, JavaScript, Bash, PHP, FastMCP, Hatchet, MCP, Kubeflow Pipelines, KServe, scikit-learn, TensorFlow/Keras, pandas, ReactJS, NodeJS, NestJS, Django
