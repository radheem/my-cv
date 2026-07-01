---
tagline: "Senior O-RAN & Telecommunications Software Engineer"
---

## Experience

### Al Hilal Invest - Senior Software Engineer
Pakistan | 11/2023 - 03/2024
- Improved deployment processes and dockerized backend services, streamlining infrastructure provisioning and container orchestration on AWS EC2 and Kubernetes.
- Led system design and code reviews to ensure architectural consistency, scalability, and reliability across distributed NodeJS, PHP, and TypeScript services.
- Developed and documented new services and features, integrating MySQL and MongoDB data stores with AWS S3 for secure object storage.
- Tech: NodeJS, PHP, TypeScript, ReactJS, Docker, MySQL, MongoDB, AWS S3, AWS EC2, Kubernetes.

### Bluefin Exchange - Senior Software Engineer
Pakistan | 06/2021 - 08/2023
- Integrated Prometheus logging, OpenTelemetry metrics, and Grafana alerts to monitor transaction engine throughput and Kafka consumer group lag, reducing latency spikes and enhancing real-time system observability.
- Identified system design improvements and proposed solutions independently, maintaining rigorous release processes and architectural documentation for core exchange services.
- Reviewed code and design decisions as a system expert for select services, while leading teams of junior engineers on high-impact project initiatives.
- Tech: ReactJS, NodeJS, Go, Python, TypeScript, Docker, PostgreSQL, DynamoDB, Kafka, Terraform, Kubernetes, Prometheus, Grafana, OpenTelemetry.

### Seed Labs - Software Engineer
Pakistan | 06/2020 - 06/2021
- Researched solutions and proposed designs for implementation, delivering robust, containerized applications using Docker and managing relational (MySQL) and NoSQL (MongoDB) databases on AWS EC2.
- Analyzed, cleaned, and visualized data to present actionable insights to stakeholders, leveraging Python, scikit-learn, and TensorFlow for data-driven pipelines and model training.
- Delivered production-ready solutions in cross-functional teams of three under the mentorship of senior engineers, focusing on scalable backend architecture.
- Tech: Python, scikit-learn, NodeJS, TensorFlow, Docker, MongoDB, MySQL, AWS EC2.

## Education

### Technical University of Ilmenau
Master of Research, Computer Systems and Engineering | 04/2024 - Present

### National University of Computer and Engineering Sciences
Bachelor of Science, Computer Science | 06/2016 - 08/2020

## Projects

### O-RAN Testbed (Open5GS + RIC + OCUDU gNB)
- Composable single-host 5G SA testbed (Open5GS 5GC + O-RAN SC Near-RT RIC + OCUDU/srsRAN gNB, ZMQ/UHD) with Python xApps over E2 and a Kafka metrics pub/sub fan-out to InfluxDB, MongoDB, and an AIMLFW store.
- Consolidated infrastructure into Docker Compose stacks, enabling flexible gNB attachment over shared bridge networks and supporting both ZMQ virtual RF and UHD over-the-air on USRP B210 SDR.
- Integrated E2SM-KPM, E2SM-RC (handover), and E2SM-CCC protocols, with real-time cellular KPIs visualized via custom Grafana dashboards.

### O-RAN AIML Framework
- End-to-end AI/ML platform for O-RAN 5G networks (Kubeflow + KServe) driven by a custom Python client/SDK. 15-credit research project, graded 1.0 (A).
- Deployed training managers, model registries, and KServe endpoints on Kubernetes via Helm, automating the full ML lifecycle from feature groups to inference.
- Authored Kubeflow pipelines in Python (kfp) with TensorFlow/Keras and scikit-learn for QoE per-cell throughput prediction, wired to InfluxDB, Cassandra, and MinIO/LeoFS storage.

### 5G Testbed (srsRAN and Open5GS, Kubernetes)
- Kubernetes-based end-to-end 5G testbed (kubeadm) running srsRAN gNB and Open5GS core as pods, with Multus CNI multi-homing (N2/N3/N6) and ZeroMQ virtual RF.
- Integrated an O-RAN SC Near-RT RIC over E2 with Python xApps (E2SM-KPM/RC) and an ONOS SDN controller for policy-based network steering.
- Configured comprehensive Prometheus and Grafana monitoring stacks to capture real-time UPF network throughput, pod CPU profiles, and gNB radio metrics; achieved 50+ Mbps TCP throughput.

## Skills

- Languages (spoken): English (fluent), German / Deutsch (A2)
- Cloud/Infra: Kubernetes, kustomize, Skaffold, Cilium, external-dns, Docker, Helm, Terraform, AWS (EC2, RDS, DynamoDB)
- Systems/Networking: gRPC, NATS (JetStream + KV), Hatchet, Kafka, OpenTelemetry, VictoriaMetrics, Grafana, Prometheus, MCP (FastMCP)
- ML/Data: Kubeflow Pipelines, KServe, scikit-learn, TensorFlow/Keras, pandas
- Databases: PostgreSQL (sqlc), MySQL, MongoDB/DocumentDB, Dgraph, DynamoDB, BigQuery, Snowflake
- Programming Languages: Go, Python, SQL, TypeScript, JavaScript, Bash, PHP
- Web: ReactJS, NodeJS, NestJS, Django
