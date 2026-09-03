---
tagline: "Data Platform Engineer"
---

## Experience

### AiVader GmbH - Research Engineering Intern
Germany | 02/2026 - 04/2026
- Brought a containerized 5G Standalone platform (Open5GS, RIC, srsRAN) to operational readiness on a single host, making the entire deployment fully reproducible with clear runbooks.
- Integrated xApp over the E2 interface, publishing gNB telemetry to message broker for real-time SRE metrics reporting.
- Built observability and resolved platform bottlenecks.
- Tech: Kubernetes, Docker, Prometheus, Grafana, InfluxDB, Telegraf, Linux, C++, Bash.

### Al Hilal Invest - Senior Software Engineer
Pakistan | 11/2023 - 03/2024
- Dockerized backend services and streamlined deployment pipelines on AWS EC2 and Kubernetes, enhancing platform reliability and release velocity.
- Led system design and code reviews to enforce architectural standards for cloud-native microservices and containerized workloads.
- Integrated application services with AWS S3, MySQL, and MongoDB to support scalable, production-ready delivery.

### Bluefin Exchange - Senior Software Engineer
Pakistan | 06/2021 - 08/2023
- Integrated OpenTelemetry distributed tracing, Prometheus metrics, and Grafana alerting to monitor transaction engine throughput and Kafka consumer lag, significantly reducing latency spikes.
- Maintained release processes and cloud-native deployment standards across exchange services using Docker and Kubernetes.
- Led engineering teams in system design reviews and platform reliability initiatives to optimize exchange infrastructure.

## Education

### Technical University of Ilmenau
Master of Research, Computer Systems and Engineering | 04/2024 - Present

### National University of Computer and Engineering Sciences
Bachelor of Science, Computer Science | 06/2016 - 08/2020

## Projects

### O-RAN Testbed (Open5GS + RIC + OCUDU gNB)
- Architected a high-throughput Kafka metrics pub/sub pipeline where xApps publish per-UE KPM data to Kafka, with consumers fan-out to InfluxDB 3/Grafana, MongoDB, and an AIMLFW-compatible InfluxDB 2 for real-time analytics and storage.
- Engineered composable Docker Compose stacks to orchestrate the Open5GS, RIC, and OCUDU gNB components, enabling rapid, reproducible testbed deployments and streamlined integration workflows.

### My Notebook (Document RAG)
- Built a durable, retryable document-ingestion pipeline using Hatchet that orchestrates extract → chunk → embed → summarize → index workflows, featuring granular per-step timeouts and automatic retries to guarantee fault-tolerant data processing.
- Implemented real-time progress streaming over NATS JetStream and Server-Sent Events (SSE), providing transparent pipeline telemetry and enabling immediate feedback for long-running RAG indexing operations.

## Skills

- **Languages & Core:** Python, Go, SQL, TypeScript, JavaScript, Bash, PHP, English (fluent), German (A2)
- **Systems & Infrastructure:** Kubernetes, Terraform, AWS (EC2, RDS, DynamoDB, S3), Docker, Helm, kustomize, Skaffold, GitLab CI/CD, event-driven architecture, streaming, ETL/ELT pipelines, data engineering, monitoring & observability (Prometheus, Grafana, OpenTelemetry)
- **Databases & Data Engineering:** Snowflake, BigQuery, PostgreSQL (sqlc), MySQL, MongoDB, Dgraph, Kafka, NATS (JetStream + KV), gRPC, Kubeflow Pipelines, KServe, scikit-learn, TensorFlow/Keras, pandas, ReactJS, NodeJS, NestJS, Django
