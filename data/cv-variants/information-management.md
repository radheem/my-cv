---
tagline: "Senior Data & Database Systems Platform Engineer"
---

## Experience

### Al Hilal Invest - Senior Software Engineer
Pakistan | 11/2023 - 03/2024
- Led system design and code reviews for backend services, optimizing data persistence layers, architectural patterns, and database schema design.
- Dockerized and containerized backend services, improving deployment reliability, infrastructure consistency, and data service isolation.
- Developed and documented new data-driven services and features, integrating MySQL and MongoDB for robust transactional and document storage.
- Tech: NodeJS, PHP, TypeScript, ReactJS, Docker, MySQL, MongoDB, AWS S3, AWS EC2, Kubernetes.

### Bluefin Exchange - Senior Software Engineer
Pakistan | 06/2021 - 08/2023
- Identified and implemented system design improvements for high-throughput transactional engines, optimizing data flow, caching strategies, and persistence layers.
- Integrated PostgreSQL and DynamoDB for scalable transactional data storage, ensuring data integrity and low-latency query performance.
- Engineered observability pipelines using Prometheus, OpenTelemetry, and Grafana to monitor transaction engine throughput and Kafka consumer group lag, significantly reducing latency spikes.
- Maintained release processes and technical documentation for core exchange services, ensuring reliable data pipeline operations and system stability.
- Led engineering teams on project initiatives, mentoring junior developers on database design, distributed system patterns, and data architecture.
- Tech: ReactJS, NodeJS, Go, Python, TypeScript, Docker, PostgreSQL, DynamoDB, Kafka, Terraform, Kubernetes, Prometheus, Grafana, OpenTelemetry.

### Seed Labs - Software Engineer
Pakistan | 06/2020 - 06/2021
- Analyzed, cleaned, and transformed raw datasets to generate actionable analytics and visualizations for stakeholder reporting and business insights.
- Delivered data-driven solutions in cross-functional teams, leveraging Python, scikit-learn, and TensorFlow for predictive modeling and data processing.
- Researched and proposed architectural designs for data storage and processing, utilizing MySQL and MongoDB for scalable persistence and retrieval.
- Tech: Python, scikit-learn, NodeJS, TensorFlow, Docker, MongoDB, MySQL, AWS EC2.

## Education

### Technical University of Ilmenau
Master of Research, Computer Systems and Engineering | 04/2024 - Present

### National University of Computer and Engineering Sciences
Bachelor of Science, Computer Science | 06/2016 - 08/2020

## Projects

### Second Brain (Document RAG)
- Built a durable, retryable document-ingestion and ETL pipeline (extract → chunk → embed → index) using Hatchet, with per-step timeouts and OpenTelemetry instrumentation.
- Designed real-time data streaming and progress tracking over NATS JetStream + SSE (durable stream + KV current-state).
- Implemented high-performance vector search and semantic persistence with pgvector (HNSW, cosine) for efficient data retrieval.
- Deployed cloud-native on k3d with custom Grafana dashboards for pipeline analytics, observability, and system monitoring.

### cv-tailor (LLM CV/Cover Tailoring + LinkedIn Automation)
- Developed a Python CLI and FastMCP server for automated data extraction and document tailoring, using unit-tested ranking algorithms to ensure factual accuracy and guard against hallucinations.
- Engineered an automated web-scraping and Gmail alert ingestion pipeline (LinkedIn, Glassdoor, Indeed, Fraunhofer) with lightweight API fetching and data normalization.
- Integrated bi-directional Google Sheets synchronization to track, persist, and visualize job application lifecycle analytics.
- Secured sensitive documents and data in Git using client-side AES-256-GCM encryption gated on password-protected static Pages.

### Information Retrieval System (IRS) - Distributed Systems Platform
- Architected a best-effort ETL side-channel into PostgreSQL (via sqlc), Dgraph, and DocumentDB, orchestrated by Hatchet with declarative routing and Ginkgo E2E verification.
- Designed and implemented a distributed data persistence layer using native NATS JetStream for messaging and KV state, replacing legacy Dapr dependencies to improve data flow efficiency.
- Integrated multiple third-party data sources via anti-corruption adapters with CUE-based schema mapping, ensuring clean data ingestion and transactional consistency.
- Deployed on Kubernetes with Cilium and OpenTelemetry, ensuring robust data pipeline observability, distributed tracing, and system reliability.

## Skills

- Languages (spoken): English (fluent), German / Deutsch (A2)
- Databases & Persistence: PostgreSQL (sqlc), MySQL, MongoDB/DocumentDB, Dgraph, DynamoDB, BigQuery, Snowflake
- Data & ETL Orchestration: Kafka, NATS (JetStream + KV), Hatchet, pandas, Kubeflow Pipelines, data extraction pipelines
- Analytics & Observability: Grafana, OpenTelemetry, VictoriaMetrics, Prometheus, data visualization, pipeline monitoring
- Programming Languages: Go, Python, SQL, TypeScript, JavaScript, Bash, PHP
- Systems & Infrastructure: Kubernetes, kustomize, Skaffold, Cilium, external-dns, Docker, Helm, Terraform, AWS (EC2, RDS, DynamoDB)
- Web & API: ReactJS, NodeJS, NestJS, Django, gRPC, MCP (FastMCP)
