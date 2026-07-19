---
tagline: "Senior Backend & Distributed Systems Engineer"
---

## Experience

### AiVader GmbH / TU Ilmenau (ICS Group) - Research Engineering Intern (5G & Open RAN)
Germany | 02/2026 - 04/2026
- Assembled a reproducible ZeroMQ virtual RF lockstep pipeline for deterministic 5G Standalone RAN emulation, stabilizing lockstep reattach mechanics and container lifecycles.
- Engineered a custom xApp that queries gNB metrics over the E2 interface and publishes real-time telemetry to a Kafka pub-sub broker, optimizing message throughput and latency.
- Brought the multi-container open-source stack to operational readiness, debugging and fixing several operational issues.
- Tech: ZeroMQ, Kafka, Python, Go, MongoDB, InfluxDB, Docker, Linux, C++.

### Al Hilal Invest - Senior Software Engineer
Pakistan | 11/2023 - 03/2024
- Architected and containerized backend services using NodeJS, TypeScript, and Docker, streamlining deployment pipelines on AWS EC2 and Kubernetes.
- Led system design reviews and code reviews, establishing architectural standards for scalable microservices and API development.
- Developed and documented new fullstack features integrating ReactJS, MySQL, and MongoDB, improving service reliability and developer velocity.

### Bluefin Exchange - Senior Software Engineer
Pakistan | 06/2021 - 08/2023
- Engineered high-throughput transaction services in Go and NodeJS, implementing distributed system design improvements to eliminate latency spikes.
- Integrated OpenTelemetry metrics, Prometheus logging, and Grafana alerts to monitor Kafka consumer group lag and backend throughput across microservices.
- Mentored junior engineers and maintained release processes for core exchange services, ensuring robust API architecture and system observability.

## Education

### Technical University of Ilmenau
Master of Research, Computer Systems and Engineering | 04/2024 - Present

### National University of Computer and Engineering Sciences
Bachelor of Science, Computer Science | 06/2016 - 08/2020

## Projects

### cv-tailor (LLM CV/Cover Tailoring + Application Management) ([portfolio](https://radheem.github.io/my-cv/projects/cv-tailor/))
- Built a Python CLI and **FastMCP Server** that automates CV/Cover letter tailoring using unit-tested project ranking (Anthropic/Ollama) and guards against hallucinations.
- Developed an automated **Gmail alert ingestion** pipeline (LinkedIn, Glassdoor, Indeed, Fraunhofer) and lightweight guest API fetching.
- Secured documents in Git using client-side **AES-256-GCM** encryption gated on password-protected static Pages.

### Information Retrieval System (IRS) - Distributed Systems Platform ([portfolio](https://radheem.github.io/my-cv/projects/irs/))
- Built Go microservices with gRPC and gRPC-Gateway using Protobuf-first APIs, migrating off Dapr to native NATS JetStream (messaging) and NATS KV (state).
- Integrated MCP (Model Context Protocol) to expose declarative, hot-reloadable tools to LLM agents via a config-driven toolbox server.
- Orchestrated best-effort ETL pipelines with Hatchet into PostgreSQL and Dgraph, verified by Ginkgo E2E gates and monitored via OpenTelemetry distributed tracing.

## Skills

- Languages (spoken): English (fluent), Deutsch (A2)
- Distributed Systems & Messaging: NATS (JetStream + KV), Kafka, gRPC, gRPC-Gateway, Hatchet, MCP (FastMCP), Dapr, OpenTelemetry
- Backend & API Architecture: Go, Python, TypeScript, NodeJS, NestJS, REST, API Design, System Design
- Cloud & Infrastructure: Kubernetes, kustomize, Skaffold, Cilium, external-dns, Docker, Helm, Terraform, AWS (EC2, RDS, DynamoDB)
- Databases & Storage: PostgreSQL (sqlc), MySQL, MongoDB/DocumentDB, Dgraph, DynamoDB, pgvector
- Web & Frontend: ReactJS, JavaScript, Bash, PHP
- ML/Data: Kubeflow Pipelines, KServe, scikit-learn, TensorFlow/Keras, pandas
