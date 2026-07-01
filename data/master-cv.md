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
- Deployed with Kubernetes, kustomize, Skaffold, Cilium, and external-dns; integrated OpenTelemetry distributed tracing and Prometheus metric collection across all Go microservices.

### Second Brain - Self-Hosted Document RAG ([repo](https://github.com/radheem/my-notebook))
- Built a durable, retryable document-ingestion pipeline with Hatchet (extract → chunk → embed → summarize → index) with per-step timeouts and retries, instrumented with OpenTelemetry and custom Grafana dashboards.
- Designed real-time progress streaming over NATS JetStream + SSE (durable stream + KV current-state).
- Kept all inference local and private via two llama.cpp servers (chat + embeddings) behind an OpenAI-compatible API.
- Implemented vector search with pgvector (HNSW, cosine); deployed cloud-native on k3d with cert-manager TLS and ExternalDNS.

### cv-tailor - LLM CV/Cover-Letter Tailoring + LinkedIn Automation ([repo](https://github.com/radheem/cv-tailor))
- Built a Python CLI and **FastMCP Server** that automates CV/Cover letter tailoring using unit-tested project ranking (Anthropic/Ollama) and guards against hallucinations.
- Developed an automated **Gmail alert ingestion** pipeline (LinkedIn, Glassdoor, Indeed, Fraunhofer) and lightweight guest API fetching.
- Integrated a bi-directional **Google Sheets synchronization** using Google Apps Script to track job application lifecycles.
- Secured documents in Git using client-side **AES-256-GCM** encryption gated on password-protected static Pages.

### O-RAN OSC AIML Framework - AI/ML Platform Engineering ([repo](https://github.com/radheemCorp/O-RAN-AIML-deployment))
- Deployed the end-to-end AIML framework on Kubernetes with Helm (training manager, model management, KF adapter, data-extraction, KServe).
- Built a config-driven Python client/SDK automating the full ML lifecycle: feature group -> model -> pipeline -> training job -> inference.
- Authored Kubeflow training/retraining pipelines in Python (kfp) with TensorFlow/Keras and scikit-learn (QoE per-cell throughput prediction).
- Served models via KServe; wired InfluxDB feature sources, a Cassandra feature store, and MinIO/LeoFS (S3) artifact storage.
- Delivered as a 15-credit research project in the integrated communications systems group (German grade 1.0).

### O-RAN Testbed - Open5GS 5GC + Near-RT RIC + OCUDU/srsRAN gNB, Docker ([repo](https://github.com/radheemCorp/oran-testbed))
- Consolidated a single-host 5G SA testbed into composable Docker Compose stacks (core, gNB ZMQ/UHD, RIC, monitoring, pub/sub) where the 5GC and Near-RT RIC publish host ports so any number of gNBs - local or remote - can attach over shared bridge networks.
- Ran the gNB on the open-source OCUDU CU/DU (srsRAN heritage), building one image for both ZMQ virtual RF and UHD over-the-air on a USRP B210 SDR.
- Integrated the O-RAN SC Near-RT RIC over E2 with Python xApps using E2SM-KPM, E2SM-RC (incl. handover), and E2SM-CCC.
- Built a Kafka metrics pub/sub pipeline: xApps publish per-UE KPM to Kafka, fanned out to InfluxDB 3 (with custom Grafana dashboards for cellular KPIs) and MongoDB.

### 5G Testbed - srsRAN and Open5GS, Kubernetes ([repo](https://github.com/radheemCorp/srsRAN-dep-zmq))
- Built a Kubernetes-based end-to-end 5G testbed (kubeadm) running srsRAN gNB and Open5GS core as pods, with Multus CNI multi-homing (N2/N3/N6) and ZeroMQ virtual RF.
- Ran host UEs as Docker containers in network namespaces via a macvlan bridge; implemented GTP tunneling and MTU-aware routing with policy-based steering.
- Integrated an O-RAN SC Near-RT RIC over E2 with Python xApps (E2SM-KPM/RC) and an ONOS SDN controller.
- Configured comprehensive Prometheus and Grafana monitoring stacks inside the Kubernetes cluster to capture real-time UPF network throughput, pod CPU profiles, and gNB radio metrics; achieved 50+ Mbps TCP throughput.

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
- Integrated Prometheus logging, OpenTelemetry metrics, and Grafana alerts to monitor transaction engine throughput and Kafka consumer group lag, reducing latency spikes.
- Maintained release processes and documentation for a set of exchange services.
- Led teams of junior engineers on project initiatives.
- Tech: ReactJS, NodeJS, Go, Python, TypeScript, Docker, PostgreSQL, DynamoDB, Kafka, Terraform, Kubernetes, Prometheus, Grafana, OpenTelemetry.

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

## Certifications

### DeepLearning.AI
*Deep Learning Specialization (5-Course Sequence via Coursera) · 01/2020*
- Neural Networks and Deep Learning; Improving Deep Neural Networks; Structuring Machine Learning Projects; Convolutional Neural Networks (CNNs); Sequence Models (RNN/LSTM/Transformers).

### Imperial College London
*Mathematics for Machine Learning: Linear Algebra (via Coursera) · 04/2022*
- Vector spaces, coordinate transformations, matrices, projections, eigenvalues, and eigenvectors for data projection (PCA).

## Skills

- Languages (spoken): English (fluent), German / Deutsch (A2)
- Programming Languages: Go, Python, SQL, TypeScript, JavaScript, Bash, PHP
- Databases: PostgreSQL (sqlc), MySQL, MongoDB/DocumentDB, Dgraph, DynamoDB, BigQuery, Snowflake
- Cloud/Infra: Kubernetes, kustomize, Skaffold, Cilium, external-dns, Docker, Helm, Terraform, AWS (EC2, RDS, DynamoDB)
- Systems: gRPC, NATS (JetStream + KV), Hatchet, MCP (FastMCP), Kafka, Dapr, OpenTelemetry, VictoriaMetrics, Grafana
- ML/Data: Kubeflow Pipelines, KServe, scikit-learn, TensorFlow/Keras, pandas
- Web: ReactJS, NodeJS, NestJS, Django
