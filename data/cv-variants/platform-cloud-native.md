---
tagline: "Senior Cloud Platform Engineer"
---

## Experience

### Al Hilal Invest - Senior Software Engineer
Pakistan | 11/2023 - 03/2024
- Dockerized backend services and modernized deployment pipelines, significantly improving infrastructure reliability and release velocity on AWS EC2 and Kubernetes.
- Led system design and code reviews for cloud-native services, enforcing platform standards, architectural best practices, and SRE observability requirements.
- Developed and documented new platform services and features, integrating containerized workloads with AWS S3, Kubernetes orchestration, and MySQL/MongoDB storage layers.

### Bluefin Exchange - Senior Software Engineer
Pakistan | 06/2021 - 08/2023
- Architected and implemented infrastructure-as-code solutions using Terraform, managing Kubernetes clusters and containerized deployments for high-throughput exchange microservices.
- Maintained robust release processes and platform documentation, streamlining GitOps workflows and enhancing SRE monitoring across distributed Go/Python services.
- Reviewed system design and code decisions as a platform expert, optimizing Docker-based deployments and Kafka event-driven pipelines for scalability, fault tolerance, and networking efficiency.
- Led engineering teams on platform initiatives, mentoring junior engineers on cloud-native best practices, infrastructure standards, and distributed systems design.

### Seed Labs - Software Engineer
Pakistan | 06/2020 - 06/2021
- Containerized data processing pipelines using Docker and deployed them on AWS EC2, establishing foundational cloud infrastructure and DevOps practices.
- Researched and proposed scalable system designs, delivering platform-ready solutions in collaborative engineering teams under senior mentorship.
- Analyzed and processed large-scale datasets, building automated data pipelines that integrated with cloud-native storage and compute resources for stakeholder reporting.

## Education

### Technical University of Ilmenau
Master of Research, Computer Systems and Engineering | 04/2024 - Present

### National University of Computer and Engineering Sciences
Bachelor of Science, Computer Science | 06/2016 - 08/2020

## Projects

### cv-tailor - LLM CV/Cover-Letter Tailoring + LinkedIn Automation
- Built a Python CLI and FastMCP Server that automates CV/Cover letter tailoring using unit-tested project ranking (Anthropic/Ollama) and guards against hallucinations.
- Developed an automated Gmail alert ingestion pipeline (LinkedIn, Glassdoor, Indeed, Fraunhofer) and lightweight guest API fetching.
- Integrated a bi-directional Google Sheets synchronization using Google Apps Script to track job application lifecycles.
- Secured documents in Git using client-side AES-256-GCM encryption gated on password-protected static Pages.

### Second Brain - Self-Hosted Document RAG
- Built a durable, retryable document-ingestion pipeline with Hatchet (extract → chunk → embed → summarize → index) with per-step timeouts and retries that survives worker crashes.
- Designed real-time progress streaming over NATS JetStream + SSE (durable stream + KV current-state).
- Kept all inference local and private via two llama.cpp servers (chat + embeddings) behind an OpenAI-compatible API.
- Implemented vector search with pgvector (HNSW, cosine); deployed cloud-native on k3d with cert-manager TLS and ExternalDNS.

### Information Retrieval System (IRS) - Distributed Systems Platform
- Built Go microservices with gRPC and gRPC-Gateway using Protobuf-first APIs and Buf tooling.
- Migrated the platform off Dapr to native NATS JetStream (messaging), NATS KV (session state), and direct gRPC.
- Built an MCP (Model Context Protocol) integration exposing the platform to LLM agents as declarative, hot-reloadable tools via a config-driven toolbox server.
- Built a per-user authenticated browser-session service (Playwright) with gateway consistent-hashing and an AES-256-GCM credential vault.
- Built a best-effort ETL side-channel into PostgreSQL (sqlc), Dgraph, and DocumentDB, orchestrated by Hatchet with declarative routing; verified by a Ginkgo E2E gate.
- Integrated multiple bot-protected third-party vendors via an adaptor/anti-corruption contract with CUE-based schema mapping.
- Deployed with Kubernetes, kustomize, Skaffold, Cilium, and external-dns.

## Skills

- Languages (spoken): English (fluent), Deutsch (A2)
- Cloud & Platform Infrastructure: Kubernetes, Cilium, Docker, Helm, kustomize, Skaffold, external-dns, Terraform, AWS (EC2, RDS, DynamoDB)
- Networking & Distributed Systems: NATS (JetStream + KV), Kafka, gRPC, OpenTelemetry, Multus CNI, ZeroMQ, E2SM protocols
- DevOps & SRE: GitOps, CI/CD pipelines, observability (VictoriaMetrics, Grafana), Hatchet, cert-manager, SRE best practices
- Programming Languages: Go, Python, SQL, TypeScript, JavaScript, Bash, PHP
- Databases: PostgreSQL (sqlc), MySQL, MongoDB/DocumentDB, Dgraph, DynamoDB, BigQuery, Snowflake
- ML & Data Platforms: Kubeflow Pipelines, KServe, scikit-learn, TensorFlow/Keras, pandas, pgvector
- Web & Application: ReactJS, NodeJS, NestJS, Django, FastMCP
