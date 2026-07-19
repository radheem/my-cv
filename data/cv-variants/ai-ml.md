---
tagline: "AI & MLOps Platform Engineer"
---

## Experience

### AiVader GmbH - Research Engineering Intern
Germany | 02/2026 - 04/2026
- Integrated and deployed a reproducible 5G Standalone (SA) testbed O RAN AI/ML Framework with runbook-configured deployments.
- Developed xApp to extract live radio performance telemetry over E2 interface and publish it to a message broker, providing a high-fidelity data source for AI/ML extraction.
- Trained and deployed QoE throughput prediction models using Kubeflow Pipelines and KServe, enabling real-time inference.
- Tech: Kubeflow, KServe, Cassandra, Python, InfluxDB, Kafka, Kubernetes, Docker, Linux.

### Al Hilal Invest - Senior Software Engineer
Pakistan | 11/2023 - 03/2024
- Architected and containerized backend services on Kubernetes and AWS, streamlining deployment pipelines for scalable platform infrastructure.
- Led system design and code reviews, establishing robust architectural patterns for distributed microservices and cloud-native deployments.
- Developed and documented high-performance services using NodeJS, TypeScript, and Docker, ensuring reliable backend operations.

### Bluefin Exchange - Senior Software Engineer
Pakistan | 06/2021 - 08/2023
- Integrated OpenTelemetry, Prometheus, and Grafana across distributed Go/Python services to monitor system throughput and reduce latency spikes.
- Identified and implemented system design improvements for core exchange services, optimizing infrastructure reliability and observability.
- Maintained release processes and led junior engineering teams, ensuring consistent deployment standards and platform stability.

## Education

### Technical University of Ilmenau
Master of Research, Computer Systems and Engineering | 04/2024 - Present

### National University of Computer and Engineering Sciences
Bachelor of Science, Computer Science | 06/2016 - 08/2020

## Projects

### My Notebook (Document RAG) ([portfolio](https://radheem.github.io/my-cv/projects/my-notebook/))
- Durable, retryable document-ingestion pipeline with Hatchet (extract → chunk → embed → summarize → index) featuring per-step timeouts, retries, and OpenTelemetry instrumentation.
- Real-time progress streaming over NATS JetStream + SSE, with all local inference secured via two llama.cpp servers behind an OpenAI-compatible API.
- Vector search implemented with pgvector (HNSW, cosine); deployed cloud-native on k3d with cert-manager TLS and ExternalDNS.

### Data Analyzer ([portfolio](https://radheem.github.io/my-cv/projects/data-analyzer/))
- Built a Python Model Context Protocol (MCP) server using `FastMCP` to expose optimized BigQuery tools to LLM agents, eliminating raw SQL token spikes and securing dataset access.
- Orchestrated Docker Compose synchronization between the custom Python FastMCP server, Grafana, and the official Grafana MCP server to enable declarative, agentic control over dashboards.
- Automated zero-touch provisioning of GCP credentials, Grafana Service Accounts, and BigQuery datasources on boot to establish immediate operational readiness.

## Skills

- Languages (spoken): English (fluent), German / Deutsch (A2)
- AI/ML & MLOps: Kubeflow Pipelines, KServe, scikit-learn, TensorFlow/Keras, pandas, pgvector, vector-search, inference, model-training, agentic agents, LLM orchestration, RAG pipelines
- Cloud & Infrastructure: Kubernetes, Helm, kustomize, Skaffold, Docker, Terraform, AWS (EC2, RDS, DynamoDB), Cilium, external-dns
- Systems & Messaging: gRPC, NATS (JetStream + KV), Hatchet, MCP (FastMCP), Kafka, Dapr, OpenTelemetry, VictoriaMetrics, Grafana
- Databases: PostgreSQL (sqlc), MySQL, MongoDB/DocumentDB, Dgraph, DynamoDB, BigQuery, Snowflake
- Programming Languages: Python, Go, SQL, TypeScript, JavaScript, Bash, PHP
- Web & Frameworks: ReactJS, NodeJS, NestJS, Django
