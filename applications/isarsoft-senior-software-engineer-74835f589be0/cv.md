---
tagline: "Senior Software Engineer"
---

## Experience

### AiVader GmbH - Research Engineering Intern
Germany | 02/2026 - 04/2026
- Containerized and deployed a full-stack 5G testbed with Docker Compose, integrating Open5GS 5GC, O-RAN SC RIC, and srsRAN/OCUDU gNB components.
- Built the Kafka-to-InfluxDB-MongoDB fan-out data pipeline and Grafana dashboards for real-time KPM visualization.
- Tech: Docker, Docker Compose, Kafka, InfluxDB, Grafana, Python, Kubernetes, Linux, C++.

### Al Hilal Invest - Senior Software Engineer
Pakistan | 11/2023 - 03/2024
- Developed and shipped fullstack features using ReactJS, NodeJS, TypeScript, NestJS, and PHP, connecting the UI through REST APIs to MySQL and MongoDB.
- Dockerized backend services and streamlined deployment pipelines on AWS EC2 and Kubernetes.
- Led system design and code reviews across frontend and backend teams.

### Bluefin Exchange - Senior Software Engineer
Pakistan | 06/2021 - 08/2023
- Built and maintained ReactJS frontend and NodeJS/Go backend services for a high-throughput trading platform.
- Integrated OpenTelemetry, Prometheus, and Grafana to monitor engine throughput and Kafka consumer lag.
- Mentored junior engineers and maintained release coordination for frontend and backend teams.

## Education

### Technical University of Ilmenau
Master of Research, Computer Systems and Engineering | 04/2024 - Present

### National University of Computer and Engineering Sciences
Bachelor of Science, Computer Science | 06/2016 - 08/2020

## Projects

### My Notebook (Document RAG) ([portfolio](https://radheem.github.io/my-cv/projects/my-notebook/))
- Built and shipped a fullstack RAG application: FastAPI backend (Python) with Next.js frontend for document upload, semantic search, and chat.
- Designed a durable, retryable ingestion pipeline (Hatchet → extract → chunk → embed → summarize → index) streaming progress via NATS JetStream + SSE.
- Implemented pgvector (HNSW, cosine) for semantic search; all inference served privately by llama.cpp.

### cv-tailor (LLM CV/Cover Tailoring) ([portfolio](https://radheem.github.io/my-cv/projects/cv-tailor/))
- Built a Python CLI and FastMCP Server that automates CV/Cover letter tailoring with unit-tested project ranking (Anthropic/Ollama).
- Developed automated Gmail alert ingestion pipelines (LinkedIn, Glassdoor, Indeed) and bi-directional Google Sheets lifecycle tracking.
- Integrated MkDocs Material static site, GitHub Actions CI/CD, and client-side AES-256-GCM document encryption.

### Sheet Dashboard ([portfolio](https://radheem.github.io/my-cv/projects/csv-dashboard/))
- Built a zero-backend web app that turns any Google Sheet into a live dashboard with client-side CSV parsing, KPI cards, and charts.
- Implemented an extensible data-type registry and charting components entirely in vanilla JavaScript.

## Skills

- Languages: English (fluent), Deutsch (A2)
- Frontend: ReactJS, Next.js, TypeScript, JavaScript, Vanilla JS, HTML5, CSS
- Backend: Go, Python, NodeJS, NestJS, Django, FastAPI, REST, gRPC
- Databases: PostgreSQL (sqlc), MySQL, MongoDB/DocumentDB, Dgraph, DynamoDB, BigQuery, Snowflake, pgvector
- Cloud/Infra: Kubernetes, Docker, Helm, kustomize, Skaffold, CI/CD (GitHub Actions), Terraform, AWS (EC2, S3)
- Messaging & Observability: NATS (JetStream + KV), Kafka, OpenTelemetry, Prometheus, VictoriaMetrics, Grafana
- ML/Data: Kubeflow, KServe, scikit-learn, TensorFlow/Keras, pandas
- Programming Languages: Go, Python, SQL, TypeScript, JavaScript, Bash, PHP
