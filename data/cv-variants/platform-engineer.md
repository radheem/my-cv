---
tagline: "Senior Cloud Platform & Observability Engineer"
---

## Experience

### Al Hilal Invest - Senior Software Engineer
Pakistan | 11/2023 - 03/2024
- Containerized and orchestrated backend services using Docker and Kubernetes, standardizing deployment pipelines and improving platform reliability across microservices.
- Architected and documented scalable cloud infrastructure on AWS (EC2, S3), conducting system design reviews to enhance platform resilience and fault tolerance.
- Streamlined DevOps workflows and release processes, reducing deployment friction and establishing consistent engineering practices for the platform team.
Tech: Kubernetes, Docker, AWS (EC2, S3), NodeJS, TypeScript, PHP, ReactJS, MySQL, MongoDB

### Bluefin Exchange - Senior Software Engineer
Pakistan | 06/2021 - 08/2023
- Engineered comprehensive observability stacks integrating Prometheus, OpenTelemetry, and Grafana to monitor transaction engine throughput and Kafka consumer group lag, proactively mitigating latency spikes and ensuring SRE reliability targets.
- Designed and maintained robust release processes and platform documentation, establishing DevOps best practices for continuous integration and deployment.
- Led system architecture reviews and code reviews for critical exchange services, optimizing Go/Node.js microservices for cloud-native scalability and operational reliability.
Tech: Kubernetes, Docker, Prometheus, OpenTelemetry, Grafana, Kafka, Terraform, Go, Python, NodeJS, PostgreSQL, DynamoDB, ReactJS, TypeScript

### Seed Labs - Software Engineer
Pakistan | 06/2020 - 06/2021
- Containerized data processing and ML workloads using Docker, deploying them on AWS EC2 infrastructure to support scalable cloud-native architectures.
- Researched and implemented distributed system designs, collaborating in agile teams to deliver reliable, data-driven backend solutions under senior mentorship.
- Automated data ingestion and visualization pipelines, establishing foundational DevOps practices for reproducible engineering workflows and platform stability.
Tech: Docker, AWS EC2, Python, NodeJS, TensorFlow, scikit-learn, MongoDB, MySQL

## Education

### Technical University of Ilmenau
Master of Research, Computer Systems and Engineering | 04/2024 - Present

### National University of Computer and Engineering Sciences
Bachelor of Science, Computer Science | 06/2016 - 08/2020

## Projects

- **Information Retrieval System (IRS) - Distributed Systems Platform**
  - Deployed and managed a cloud-native platform on Kubernetes with kustomize, Skaffold, Cilium, and external-dns, ensuring robust networking, DNS resolution, and platform reliability.
  - Integrated OpenTelemetry distributed tracing and Prometheus metric collection across all Go microservices, establishing comprehensive observability and SRE monitoring baselines.
  - Migrated messaging and state management from Dapr to native NATS JetStream and KV, optimizing platform reliability and reducing operational overhead.
  - Orchestrated declarative ETL pipelines with Hatchet and verified reliability via Ginkgo E2E gates, ensuring data consistency across PostgreSQL, Dgraph, and DocumentDB.

- **Second Brain - Self-Hosted Document RAG**
  - Built a durable, retryable document-ingestion pipeline with Hatchet, instrumented with OpenTelemetry and custom Grafana dashboards for real-time observability and metrics tracking.
  - Designed real-time progress streaming over NATS JetStream + SSE, implementing durable streams and KV current-state tracking for platform reliability and state management.
  - Deployed cloud-native on k3d with cert-manager TLS and ExternalDNS, maintaining local llama.cpp inference servers behind an OpenAI-compatible API for secure, private processing.
  - Implemented vector search with pgvector (HNSW, cosine), optimizing semantic retrieval performance within a self-hosted Kubernetes homelab environment.

- **cv-tailor - LLM CV/Cover-Letter Tailoring + LinkedIn Automation**
  - Developed a Python CLI and FastMCP Server that automates CV/Cover letter tailoring using unit-tested project ranking, ensuring reliable LLM output generation and platform security.
  - Engineered an automated Gmail alert ingestion pipeline (LinkedIn, Glassdoor, Indeed, Fraunhofer) and lightweight guest API fetching, integrating bi-directional Google Sheets synchronization for lifecycle tracking.
  - Secured sensitive documents in Git using client-side AES-256-GCM encryption gated on password-protected static Pages, enforcing platform data integrity and access control standards.

## Skills

- Languages (spoken): English (fluent), German / Deutsch (A2)
- Cloud & Platform Infrastructure: Kubernetes, Docker, Helm, kustomize, Skaffold, Cilium, external-dns, Terraform, AWS (EC2, RDS, DynamoDB)
- Observability, Monitoring & SRE: OpenTelemetry, Prometheus, VictoriaMetrics, Grafana, distributed tracing, metrics collection, reliability engineering, alerting
- Networking & Distributed Systems: gRPC, NATS (JetStream + KV), Kafka, Dapr, ebpf/Cilium networking, DNS resolution
- Programming Languages: Go, Python, SQL, TypeScript, JavaScript, Bash, PHP
- Databases & Storage: PostgreSQL (sqlc), MySQL, MongoDB/DocumentDB, Dgraph, DynamoDB, BigQuery, Snowflake
- ML & Data Engineering: Kubeflow Pipelines, KServe, scikit-learn, TensorFlow/Keras, pandas
- Web & Backend Frameworks: ReactJS, NodeJS, NestJS, Django
