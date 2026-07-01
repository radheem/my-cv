---
tagline: "Internship in Technology, Data & Innovation"
---

## Experience

### Al Hilal Invest - Senior Software Engineer
Pakistan | 11/2023 - 03/2024
- Containerized backend services with Docker and orchestrated deployments on AWS EC2 and Kubernetes, streamlining release pipelines and platform scalability.
- Led platform architecture reviews and code quality standards, focusing on scalable infrastructure, DevOps practices, and system reliability.
- Developed and documented cloud-native service integrations, ensuring high availability and robust deployment processes.
Tech: NodeJS, PHP, TypeScript, ReactJS, Docker, MySQL, MongoDB, AWS S3, AWS EC2, Kubernetes.

### Bluefin Exchange - Senior Software Engineer
Pakistan | 06/2021 - 08/2023
- Engineered comprehensive observability stacks using Prometheus, OpenTelemetry, and Grafana to monitor transaction engine throughput and Kafka consumer lag, proactively reducing latency spikes and improving platform reliability.
- Orchestrated CI/CD release processes and infrastructure-as-code (Terraform) for Kubernetes-based microservices, enforcing GitOps principles and platform stability.
- Designed and implemented scalable platform architectures, optimizing distributed systems for high availability and low-latency performance.
- Served as platform subject-matter expert for system design reviews, ensuring adherence to SRE best practices and observability standards.
- Mentored engineering teams on cloud-native development, Kubernetes operations, and observability-driven debugging.
Tech: ReactJS, NodeJS, Go, Python, TypeScript, Docker, PostgreSQL, DynamoDB, Kafka, Terraform, Kubernetes, Prometheus, Grafana, OpenTelemetry.

### Seed Labs - Software Engineer
Pakistan | 06/2020 - 06/2021
- Collaborated in cross-functional engineering teams to deliver containerized applications using Docker and AWS EC2 infrastructure, focusing on automated deployment workflows.
- Researched and prototyped scalable backend architectures and automation scripts to streamline data pipeline deployments and platform integration.
- Developed automated data processing pipelines and visualization dashboards, integrating infrastructure metrics for operational transparency and reliability tracking.
Tech: Python, scikit-learn, NodeJS, TensorFlow, Docker, MongoDB, MySQL, AWS EC2.

## Education

### Technical University of Ilmenau
Master of Research, Computer Systems and Engineering | 04/2024 - Present

### National University of Computer and Engineering Sciences
Bachelor of Science, Computer Science | 06/2016 - 08/2020

## Projects

### cv-tailor - LLM CV/Cover-Letter Tailoring + LinkedIn Automation
- Built a Python CLI and FastMCP Server that automates CV/Cover letter tailoring using unit-tested project ranking (Anthropic/Ollama) and guards against hallucinations.
- Developed an automated Gmail alert ingestion pipeline (LinkedIn, Glassdoor, Indeed, Fraunhofer) and lightweight guest API fetching, ensuring reliable data synchronization and platform state management.
- Integrated a bi-directional Google Sheets synchronization using Google Apps Script to track job application lifecycles and automate workflow transitions.
- Secured documents in Git using client-side AES-256-GCM encryption gated on password-protected static Pages, enforcing zero-trust data handling and platform security.

### Second Brain - Self-Hosted Document RAG
- Built a durable, retryable document-ingestion pipeline with Hatchet (extract → chunk → embed → summarize → index) with per-step timeouts and retries, instrumented with OpenTelemetry and custom Grafana dashboards.
- Designed real-time progress streaming over NATS JetStream + SSE (durable stream + KV current-state), ensuring reliable event-driven communication and platform observability.
- Kept all inference local and private via two llama.cpp servers (chat + embeddings) behind an OpenAI-compatible API, optimizing platform resource utilization and network isolation.
- Implemented vector search with pgvector (HNSW, cosine); deployed cloud-native on k3d with cert-manager TLS and ExternalDNS, ensuring secure DNS resolution and platform availability.

### Information Retrieval System (IRS) - Distributed Systems Platform
- Deployed with Kubernetes, kustomize, Skaffold, Cilium, and external-dns; integrated OpenTelemetry distributed tracing and Prometheus metric collection across all Go microservices.
- Migrated the platform off Dapr to native NATS JetStream (messaging), NATS KV (session state), and direct gRPC, reducing platform overhead and improving networking reliability.
- Built a best-effort ETL side-channel into PostgreSQL (sqlc), Dgraph, and DocumentDB, orchestrated by Hatchet with declarative routing; verified by a Ginkgo E2E gate.
- Built Go microservices with gRPC and gRPC-Gateway using Protobuf-first APIs and Buf tooling, establishing a robust, observable platform foundation with consistent-hashing gateways.

## Skills

- Languages (spoken): English (fluent), German / Deutsch (A2)
- Cloud & Platform Infra: Kubernetes, Cilium, Docker, Helm, kustomize, Skaffold, external-dns, Terraform, AWS (EC2, RDS, DynamoDB)
- Observability & SRE: OpenTelemetry, Prometheus, Grafana, VictoriaMetrics, distributed tracing, metrics collection, alerting, reliability engineering
- Networking & Messaging: NATS (JetStream + KV), Kafka, gRPC, Dapr
- Programming Languages: Go, Python, SQL, TypeScript, JavaScript, Bash, PHP
- Databases: PostgreSQL (sqlc), MySQL, MongoDB/DocumentDB, Dgraph, DynamoDB, BigQuery, Snowflake
- Web: ReactJS, NodeJS, NestJS, Django
- ML/Data: Kubeflow Pipelines, KServe, scikit-learn, TensorFlow/Keras, pandas
