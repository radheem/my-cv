# Radheem Bin Razi

Ilmenau, Germany | +49 155 60115132 | sheikh.radheem@gmail.com

<!-- SOURCE OF TRUTH (facts) for tailored CVs. Real data — private repo.
     Never invent roles, employers, dates, skills, or metrics beyond what is here. -->

## Summary
Software engineer with 5 years of experience across distributed systems, cloud-native platforms, and data-driven backends. Delivered microservices, event-driven pipelines, and ML infrastructure using Go, Python, and Kubernetes. Experienced in system design, documentation, and mentoring.

## Selected Work

### Information Retrieval System (IRS) - Distributed Systems Platform (Stealth Project)
- Built Go microservices with gRPC and gRPC-Gateway using Protobuf-first APIs and Buf tooling.
- Migrated the platform off Dapr to native NATS JetStream (messaging), NATS KV (session state), and direct gRPC.
- Built an MCP (Model Context Protocol) integration exposing the platform to LLM agents as declarative, hot-reloadable tools via a config-driven toolbox server.
- Built a per-user authenticated browser-session service (Playwright) with gateway consistent-hashing and an AES-256-GCM credential vault.
- Built a best-effort ETL side-channel into PostgreSQL (sqlc), Dgraph, and DocumentDB, orchestrated by Hatchet with declarative routing; verified by a Ginkgo E2E gate.
- Integrated multiple bot-protected third-party vendors via an adaptor/anti-corruption contract with CUE-based schema mapping.
- Deployed with Kubernetes, kustomize, Skaffold, Cilium, and external-dns.

### Second Brain - Self-Hosted Document RAG ([repo](https://github.com/radheem/my-notebook))
- Built a durable, retryable document-ingestion pipeline with Hatchet (extract → chunk → embed → summarize → index) with per-step timeouts and retries that survives worker crashes.
- Designed real-time progress streaming over NATS JetStream + SSE (durable stream + KV current-state).
- Kept all inference local and private via two llama.cpp servers (chat + embeddings) behind an OpenAI-compatible API.
- Implemented vector search with pgvector (HNSW, cosine); deployed cloud-native on k3d with cert-manager TLS and ExternalDNS.

### O-RAN OSC AIML Framework - AI/ML Platform Engineering ([repo](https://github.com/radheemCorp/O-RAN-AIML-deployment))
- Deployed the end-to-end AIML framework on Kubernetes with Helm (training manager, model management, KF adapter, data-extraction, KServe).
- Built a config-driven Python client/SDK automating the full ML lifecycle: feature group -> model -> pipeline -> training job -> inference.
- Authored Kubeflow training/retraining pipelines in Python (kfp) with TensorFlow/Keras and scikit-learn (QoE per-cell throughput prediction).
- Served models via KServe; wired InfluxDB feature sources, a Cassandra feature store, and MinIO/LeoFS (S3) artifact storage.
- Delivered as a 15-credit research project in the integrated communications systems group (German grade 1.0).

### 5G srsRAN + O-RAN RIC Testbed, Docker ([repo](https://github.com/radheemCorp/srsran-docker))
- Built a single-host Dockerized 5G SA lab: srsRAN gNB (ZMQ/UHD), Open5GS core, and an integrated O-RAN SC Near-RT RIC.
- Integrated the RIC platform with the gNB over E2 and developed Python xApps using E2SM-KPM, E2SM-RC (incl. handover), and E2SM-CCC.
- Built a Telegraf -> InfluxDB -> Grafana pipeline with a custom writer persisting per-UE KPM metrics.

### 5G Testbed - srsRAN and Open5GS, Kubernetes ([repo](https://github.com/radheemCorp/srsRAN-dep-zmq))
- Built a Kubernetes-based end-to-end 5G testbed (kubeadm) running srsRAN gNB and Open5GS core as pods, with Multus CNI multi-homing (N2/N3/N6) and ZeroMQ virtual RF.
- Ran host UEs as Docker containers in network namespaces via a macvlan bridge; implemented GTP tunneling and MTU-aware routing with policy-based steering.
- Integrated an O-RAN SC Near-RT RIC over E2 with Python xApps (E2SM-KPM/RC) and an ONOS SDN controller.
- Added Prometheus/Grafana observability; achieved 50+ Mbps TCP throughput and validated UE-to-UE hairpin routing via UPF.

## Experience

### Al Hilal Invest - Senior Software Engineer
Pakistan | 11/2023 - 03/2024
- Developed and documented new services and features.
- Led system design reviews and code reviews.
- Improved deployment processes and dockerized backend services.
- Tech: NodeJS, PHP, TypeScript, ReactJS, Docker, MySQL, MongoDB, AWS S3, AWS EC2, Kubernetes.

### Bluefin Exchange - Senior Software Engineer
Pakistan | 06/2021 - 08/2023
- Identified system design improvements and proposed solutions independently.
- Reviewed code and design decisions as a system expert for select services.
- Maintained release processes and documentation for a set of exchange services.
- Led teams of junior engineers on project initiatives.
- Tech: ReactJS, NodeJS, Go, Python, TypeScript, Docker, PostgreSQL, DynamoDB, Kafka, Terraform, Kubernetes.

### Seed Labs - Software Engineer
Pakistan | 06/2020 - 06/2021
- Researched solutions and proposed designs for implementation.
- Delivered solutions in teams of three under mentorship of senior engineers.
- Analyzed, cleaned, and visualized data to present insights to stakeholders.
- Tech: Python, scikit-learn, NodeJS, TensorFlow, Docker, MongoDB, MySQL, AWS EC2.

## Education

### Technical University of Ilmenau
Master of Research, Computer Systems and Engineering | 04/2024 - Present

### National University of Computer and Engineering Sciences
Bachelor of Science, Computer Science | 06/2016 - 08/2020

## Skills

- Languages (spoken): English (fluent), German / Deutsch (A2)
- Programming Languages: Go, Python, TypeScript, JavaScript, PHP
- Databases: PostgreSQL (sqlc), MySQL, MongoDB/DocumentDB, Dgraph, DynamoDB, BigQuery, Snowflake
- Cloud/Infra: Kubernetes, kustomize, Skaffold, Cilium, external-dns, Docker, Helm, Terraform, AWS (EC2, RDS, DynamoDB)
- Systems: gRPC, NATS (JetStream + KV), Hatchet, MCP, Kafka, Dapr, OpenTelemetry, VictoriaMetrics, Grafana
- ML/Data: Kubeflow Pipelines, KServe, scikit-learn, TensorFlow/Keras, pandas
- Web: ReactJS, NodeJS, NestJS, Django
