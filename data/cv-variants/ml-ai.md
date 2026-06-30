---
tagline: "AI & MLOps Platform Engineer"
---

## Experience

### Al Hilal Invest - Senior Software Engineer
Pakistan | 11/2023 - 03/2024
- Dockerized backend services and streamlined deployment pipelines to improve platform scalability and infrastructure reliability.
- Led system design and code reviews, establishing architectural standards for distributed microservices and platform integration.
- Developed and documented new platform services and features, ensuring robust backend connectivity and operational consistency.
- Tech: NodeJS, PHP, TypeScript, ReactJS, Docker, MySQL, MongoDB, AWS S3, AWS EC2, Kubernetes.

### Bluefin Exchange - Senior Software Engineer
Pakistan | 06/2021 - 08/2023
- Architected and maintained release processes and documentation for high-throughput exchange services, ensuring platform stability.
- Identified system design improvements and proposed scalable solutions for distributed backend infrastructure and data pipelines.
- Led technical initiatives and mentored junior engineers, overseeing code reviews, design decisions, and platform best practices.
- Tech: ReactJS, NodeJS, Go, Python, TypeScript, Docker, PostgreSQL, DynamoDB, Kafka, Terraform, Kubernetes.

### Seed Labs - Software Engineer
Pakistan | 06/2020 - 06/2021
- Researched and implemented data-driven solutions, leveraging Python, scikit-learn, and TensorFlow for machine learning workflows and algorithmic development.
- Analyzed, cleaned, and visualized complex datasets to derive actionable insights, model performance metrics, and stakeholder reports.
- Delivered collaborative engineering solutions under senior mentorship, focusing on model integration, pipeline implementation, and system architecture.
- Tech: Python, scikit-learn, NodeJS, TensorFlow, Docker, MongoDB, MySQL, AWS EC2.

## Education

### Technical University of Ilmenau
Master of Research, Computer Systems and Engineering | 04/2024 - Present

### National University of Computer and Engineering Sciences
Bachelor of Science, Computer Science | 06/2016 - 08/2020

## Projects

### Second Brain (Document RAG) — Self-hosted RAG document-intelligence service: durable Hatchet ingestion, local llama.cpp inference, pgvector semantic search, NATS JetStream progress streaming on a k3d homelab.
- Built a durable, retryable document-ingestion pipeline with Hatchet (extract → chunk → embed → summarize → index) with per-step timeouts and retries, instrumented with OpenTelemetry and custom Grafana dashboards.
- Designed real-time progress streaming over NATS JetStream + SSE (durable stream + KV current-state).
- Monitored pipeline latency and GPU/VRAM consumption on llama.cpp servers using Grafana, optimizing chunking/embedding batch sizes for local inference.
- Implemented vector search with pgvector (HNSW, cosine); deployed cloud-native on k3d with cert-manager TLS and ExternalDNS.
([repo](https://github.com/radheem/my-notebook))

### cv-tailor (LLM CV/Cover Tailoring + LinkedIn Automation) — Python CLI tool and FastMCP server that turns a job posting into a tailored CV + cover letter: pure ranker picks facts and LLM only writes prose, with automated multi-source Gmail alert ingestion (LinkedIn, Indeed, Glassdoor, Fraunhofer), and Google Sheets lifecycle syncing.
- Built a Python CLI and **FastMCP Server** that automates CV/Cover letter tailoring using unit-tested project ranking (Anthropic/Ollama) and guards against hallucinations.
- Developed an automated **Gmail alert ingestion** pipeline (LinkedIn, Glassdoor, Indeed, Fraunhofer) and lightweight guest API fetching.
- Integrated a bi-directional **Google Sheets synchronization** using Google Apps Script to track job application lifecycles.
- Secured documents in Git using client-side **AES-256-GCM** encryption gated on password-protected static Pages.
([repo](https://github.com/radheem/cv-tailor))

### O-RAN AIML Framework — End-to-end AI/ML platform for O-RAN 5G networks (Kubeflow + KServe) driven by a custom Python client/SDK. 15-credit research project, graded 1.0 (A).
- Deployed the end-to-end AIML framework on Kubernetes with Helm (training manager, model management, KF adapter, data-extraction, KServe).
- Built a config-driven Python client/SDK automating the full ML lifecycle: feature group -> model -> pipeline -> training job -> inference.
- Authored Kubeflow training/retraining pipelines in Python (kfp) with TensorFlow/Keras and scikit-learn (QoE prediction), instrumenting training jobs with Prometheus metrics to track training duration and model loss.
- Served models via KServe; wired InfluxDB feature sources, a Cassandra feature store, and MinIO/LeoFS (S3) artifact storage.
- Delivered as a 15-credit research project in the integrated communications systems group (German grade 1.0).
([repo](https://github.com/radheemCorp/O-RAN-AIML-deployment))

## Skills

- Languages (spoken): English (fluent), Deutsch (A2)
- Programming Languages: Python, Go, SQL, TypeScript, JavaScript, Bash, PHP
- ML/AI & MLOps: Kubeflow Pipelines, KServe, scikit-learn, TensorFlow/Keras, pandas, LLM inference (llama.cpp), RAG pipelines, Vector Search (pgvector)
- Cloud/Infra & Orchestration: Kubernetes, Helm, kustomize, Skaffold, Docker, Terraform, AWS (EC2, RDS, DynamoDB)
- Data & Storage: PostgreSQL (sqlc), pgvector, MongoDB/DocumentDB, Dgraph, DynamoDB, BigQuery, Snowflake, InfluxDB, Cassandra, MinIO/LeoFS
- Systems & Messaging: NATS (JetStream + KV), Hatchet, Kafka, MCP (FastMCP), gRPC, Dapr, OpenTelemetry, VictoriaMetrics, Grafana
- Web: ReactJS, NodeJS, NestJS, Django
