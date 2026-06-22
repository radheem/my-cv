---
tagline: "Backend Engineer"
---

## Experience

### Al Hilal Invest — Senior Software Engineer
*Pakistan · 11/2023 – 03/2024*
- Developed and documented backend services and features using NodeJS, TypeScript, and ReactJS, improving deployment processes and dockerizing backend services on AWS EC2 and S3.
- Led system design and code reviews to enforce clean code practices and architectural integrity across the team.
- Improved deployment processes and dockerized backend services, leveraging MySQL and MongoDB for data persistence.

### Bluefin Exchange — Senior Software Engineer
*Pakistan · 06/2021 – 08/2023*
- Identified system design improvements and proposed solutions for exchange services using NodeJS, Go, and TypeScript.
- Reviewed code and design decisions as a system expert, mentoring junior engineers and leading teams on project initiatives.
- Maintained release processes and documentation, leveraging PostgreSQL, DynamoDB, Kafka, and Terraform for cloud-native infrastructure.

### Seed Labs — Software Engineer
*Pakistan · 06/2020 – 06/2021*
- Researched solutions and proposed designs for implementation using NodeJS and Python.
- Delivered solutions in teams of three under mentorship, analyzing, cleaning, and visualizing data to present insights to stakeholders.
- Analyzed, cleaned, and visualized data to present insights to stakeholders, utilizing AWS EC2, MongoDB, and MySQL.

## Education

### Technical University of Ilmenau
*Master of Research, Computer Systems and Engineering · 04/2024 – Present*

### National University of Computer and Engineering Sciences
*Bachelor of Science, Computer Science · 06/2016 – 08/2020*

## Projects

- **IRS Platform (Stealth)** — Built Go microservices with gRPC and gRPC-Gateway using Protobuf-first APIs, migrating off Dapr to native NATS JetStream for messaging and session state while orchestrating best-effort ETL pipelines into PostgreSQL (sqlc), Dgraph, and DocumentDB via Hatchet with declarative routing and Ginkgo E2E data-quality gates. Secured per-user browser sessions with Playwright, gateway consistent-hashing, and an AES-256-GCM credential vault, deploying the platform on Kubernetes with kustomize, Skaffold, and Cilium.
- **cv-tailor (LLM CV/Cover Tailoring + LinkedIn Automation)** — Engineered a Python-based application with a unit-tested ranker and LLM integration, versioning every application in Git with a status lifecycle surfaced on a MkDocs site. Implemented robust CI/CD with GitHub Actions to render, seal, and deploy to GitHub Pages, gating per-job documents with in-browser PBKDF2 and AES-256-GCM encryption while ensuring no API keys in CI. Added a containerized LinkedIn ingestion flow via Playwright with human-paced automation and VNC CAPTCHA hand-off, generating reproducible outputs with model/seed/prompt hash manifests guarded by quality-benchmark regression gates.
- **O-RAN Testbed (Open5GS + RIC + OCUDU gNB)** — Consolidated a 5G SA testbed into composable Docker Compose stacks for the core, gNB, RIC, and monitoring, enabling remote gNB attachment over shared bridge networks. Built a Kafka metrics pub/sub pipeline where xApps publish per-UE KPM data to Kafka, with consumers fanning messages to InfluxDB 3 (Grafana), MongoDB, and an AIMLFW-compatible InfluxDB 2. Integrated the O-RAN SC Near-RT RIC over E2 with Python xApps using E2SM-KPM, E2SM-RC, and E2SM-CCC, running the gNB on OCUDU CU/DU with a unified image for ZMQ virtual RF and UHD over-the-air on USRP B210 SDR.

## Skills

- **Languages** — English (fluent), Deutsch (A2)
- **Programming Languages** — TypeScript, Go, Python, SQL, JavaScript, Bash, PHP
- **Cloud-Native & Infra** — Kubernetes, kustomize, Skaffold, Helm, Cilium, Docker, Terraform, external-dns
- **Web & API** — NodeJS, REST, ReactJS, NestJS, Django, Protocol Buffers, OpenAPI
- **Databases & Persistence** — PostgreSQL, MySQL, MongoDB/DocumentDB, Dgraph, DynamoDB, BigQuery, Snowflake, pgvector
