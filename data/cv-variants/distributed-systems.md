---
tagline: "Senior Backend & Distributed Systems Engineer"
---

## Experience

### Al Hilal Invest - Senior Software Engineer
Pakistan | 11/2023 - 03/2024
- Led system design reviews and backend architecture decisions for scalable, cloud-native services.
- Improved deployment pipelines and containerized backend services using Docker and Kubernetes on AWS EC2.
- Developed and documented new backend services and features, ensuring robust API contracts and system reliability.
- Tech: NodeJS, PHP, TypeScript, ReactJS, Docker, MySQL, MongoDB, AWS S3, AWS EC2, Kubernetes.

### Bluefin Exchange - Senior Software Engineer
Pakistan | 06/2021 - 08/2023
- Architected and maintained high-throughput backend services using Go and Python, leveraging Kafka for event-driven messaging and distributed state management.
- Identified and implemented system design improvements to optimize microservice communication, data consistency, and backend performance across PostgreSQL and DynamoDB.
- Led engineering teams and reviewed code/design decisions, establishing standards for scalable backend architecture, release processes, and distributed system reliability.
- Tech: ReactJS, NodeJS, Go, Python, TypeScript, Docker, PostgreSQL, DynamoDB, Kafka, Terraform, Kubernetes.

### Seed Labs - Software Engineer
Pakistan | 06/2020 - 06/2021
- Researched and proposed distributed system designs and backend solutions for data-intensive applications.
- Delivered production-ready microservices and data pipelines in collaborative teams, utilizing Python and NodeJS with Dockerized deployments on AWS EC2.
- Analyzed and processed large-scale datasets to drive backend insights and system optimization.
- Tech: Python, scikit-learn, NodeJS, TensorFlow, Docker, MongoDB, MySQL, AWS EC2.

## Education

### Technical University of Ilmenau
Master of Research, Computer Systems and Engineering | 04/2024 - Present

### National University of Computer and Engineering Sciences
Bachelor of Science, Computer Science | 06/2016 - 08/2020

## Projects

### Information Retrieval System (IRS) - Distributed Systems Platform
- Built Go microservices with gRPC and gRPC-Gateway using Protobuf-first APIs and Buf tooling.
- Migrated the platform off Dapr to native NATS JetStream (messaging), NATS KV (session state), and direct gRPC.
- Built an MCP (Model Context Protocol) integration exposing the platform to LLM agents as declarative, hot-reloadable tools via a config-driven toolbox server.
- Built a per-user authenticated browser-session service (Playwright) with gateway consistent-hashing and an AES-256-GCM credential vault.
- Built a best-effort ETL side-channel into PostgreSQL (sqlc), Dgraph, and DocumentDB, orchestrated by Hatchet with declarative routing; verified by a Ginkgo E2E gate.
- Integrated multiple bot-protected third-party vendors via an adaptor/anti-corruption contract with CUE-based schema mapping.
- Deployed with Kubernetes, kustomize, Skaffold, Cilium, and external-dns.

### Second Brain - Self-Hosted Document RAG
- Built a durable, retryable document-ingestion pipeline with Hatchet (extract → chunk → embed → summarize → index) with per-step timeouts and retries that survives worker crashes.
- Designed real-time progress streaming over NATS JetStream + SSE (durable stream + KV current-state).
- Kept all inference local and private via two llama.cpp servers (chat + embeddings) behind an OpenAI-compatible API.
- Implemented vector search with pgvector (HNSW, cosine); deployed cloud-native on k3d with cert-manager TLS and ExternalDNS.

### cv-tailor - LLM CV/Cover-Letter Tailoring + LinkedIn Automation
- Built a Python CLI and **FastMCP Server** that automates CV/Cover letter tailoring using unit-tested project ranking (Anthropic/Ollama) and guards against hallucinations.
- Developed an automated **Gmail alert ingestion** pipeline (LinkedIn, Glassdoor, Indeed, Fraunhofer) and lightweight guest API fetching.
- Integrated a bi-directional **Google Sheets synchronization** using Google Apps Script to track job application lifecycles.
- Secured documents in Git using client-side **AES-256-GCM** encryption gated on password-protected static Pages.

## Skills
- Languages (spoken): English (fluent), German / Deutsch (A2)
- Programming Languages: Go, Python, SQL, TypeScript, JavaScript, Bash, PHP
- Distributed Systems & Messaging: NATS (JetStream + KV), gRPC, gRPC-Gateway, Kafka, Dapr, MCP (FastMCP), Hatchet, OpenTelemetry
- Cloud & Infrastructure: Kubernetes, kustomize, Skaffold, Cilium, external-dns, Docker, Helm, Terraform, AWS (EC2, RDS, DynamoDB)
- Databases & Storage: PostgreSQL (sqlc), MySQL, MongoDB/DocumentDB, Dgraph, DynamoDB, BigQuery, Snowflake
- ML & Data Engineering: Kubeflow Pipelines, KServe, scikit-learn, TensorFlow/Keras, pandas
- Web & Backend Frameworks: ReactJS, NodeJS, NestJS, Django
