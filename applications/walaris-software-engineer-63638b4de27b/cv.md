---
tagline: "Software Engineer"
---

## Experience

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

### Seed Labs - Software Engineer
Pakistan | 06/2020 - 06/2021
- Developed and trained machine learning models using Python, TensorFlow, and scikit-learn, focusing on data-driven predictive solutions.
- Analyzed, cleaned, and visualized complex datasets to extract actionable insights, supporting stakeholder decision-making and model validation.

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

### cv-tailor (LLM CV/Cover Tailoring + Application Management) ([portfolio](https://radheem.github.io/my-cv/projects/cv-tailor/))
- Built a Python CLI and FastMCP Server automating CV/Cover letter tailoring with unit-tested project ranking (Anthropic/Ollama) and hallucination guards.
- Developed automated Gmail alert ingestion pipelines and bi-directional Google Sheets synchronization to track job application lifecycles.
- Secured documents in Git using client-side AES-256-GCM encryption gated on password-protected static Pages.

### O-RAN AIML Framework ([portfolio](https://radheem.github.io/my-cv/projects/oran-aiml/))
- Deployed end-to-end AIML framework on Kubernetes with Helm, featuring a config-driven Python SDK automating the full ML lifecycle (feature group → training → inference).
- Authored Kubeflow training/retraining pipelines (kfp) with TensorFlow/Keras and scikit-learn, serving models via KServe with integrated feature stores and artifact storage.

## Skills

- Languages (spoken): English (fluent), German / Deutsch (A2)
- AI/ML & MLOps: Kubeflow Pipelines, KServe, scikit-learn, TensorFlow/Keras, pandas, pgvector, vector-search, inference, model-training, agentic agents, LLM orchestration, RAG pipelines
- Cloud & Infrastructure: Kubernetes, Helm, kustomize, Skaffold, Docker, Terraform, AWS (EC2, RDS, DynamoDB), Cilium, external-dns
- Systems & Messaging: gRPC, NATS (JetStream + KV), Hatchet, MCP (FastMCP), Kafka, Dapr, OpenTelemetry, VictoriaMetrics, Grafana
- Databases: PostgreSQL (sqlc), MySQL, MongoDB/DocumentDB, Dgraph, DynamoDB, BigQuery, Snowflake
- Programming Languages: Python, Go, SQL, TypeScript, JavaScript, Bash, PHP
- Web & Frameworks: ReactJS, NodeJS, NestJS, Django
