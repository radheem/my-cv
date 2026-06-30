---
tagline: "Senior O-RAN & Systems Engineer"
---

## Experience

### Al Hilal Invest - Senior Software Engineer
Pakistan | 11/2023 - 03/2024
- Led system design reviews and code reviews for distributed backend services, ensuring architectural alignment with cloud-native standards.
- Improved deployment pipelines by containerizing backend services with Docker and managing infrastructure provisioning on AWS EC2/S3 and Kubernetes.
- Tech: NodeJS, PHP, TypeScript, ReactJS, Docker, MySQL, MongoDB, AWS S3, AWS EC2, Kubernetes.

### Bluefin Exchange - Senior Software Engineer
Pakistan | 06/2021 - 08/2023
- Identified and implemented system design improvements for high-throughput exchange services, focusing on distributed architecture and scalability.
- Maintained release processes and documentation while leading junior engineering teams on project initiatives.
- Leveraged Go, Python, Kafka, and Kubernetes to optimize distributed data pipelines and infrastructure provisioning with Terraform.
- Tech: ReactJS, NodeJS, Go, Python, TypeScript, Docker, PostgreSQL, DynamoDB, Kafka, Terraform, Kubernetes.

### Seed Labs - Software Engineer
Pakistan | 06/2020 - 06/2021
- Researched and proposed system architectures for data-driven applications, delivering solutions in cross-functional teams under senior mentorship.
- Analyzed, cleaned, and visualized data to present insights to stakeholders, focusing on Python-based ML pipelines and cloud infrastructure deployment.
- Tech: Python, scikit-learn, NodeJS, TensorFlow, Docker, MongoDB, MySQL, AWS EC2.

## Education

### Technical University of Ilmenau
Master of Research, Computer Systems and Engineering | 04/2024 - Present

### National University of Computer and Engineering Sciences
Bachelor of Science, Computer Science | 06/2016 - 08/2020

## Projects

### O-RAN Testbed (Open5GS + RIC + OCUDU gNB)
Consolidated a single-host 5G SA testbed into composable Docker Compose stacks (core, gNB ZMQ/UHD, RIC, monitoring, pub/sub) where the 5GC and Near-RT RIC publish host ports so any number of gNBs - local or remote - can attach over shared bridge networks. Ran the gNB on the open-source OCUDU CU/DU (srsRAN heritage), building one image for both ZMQ virtual RF and UHD over-the-air on a USRP B210 SDR. Integrated the O-RAN SC Near-RT RIC over E2 with Python xApps using E2SM-KPM, E2SM-RC (incl. handover), and E2SM-CCC. Built a Kafka metrics pub/sub pipeline: xApps publish per-UE KPM to Kafka, fanned out to InfluxDB 3 (with custom Grafana dashboards for cellular KPIs) and MongoDB.

### O-RAN AIML Framework
Deployed the end-to-end AIML framework on Kubernetes with Helm (training manager, model management, KF adapter, data-extraction, KServe). Built a config-driven Python client/SDK automating the full ML lifecycle: feature group -> model -> pipeline -> training job -> inference. Authored Kubeflow training/retraining pipelines in Python (kfp) with TensorFlow/Keras and scikit-learn (QoE per-cell throughput prediction). Served models via KServe; wired InfluxDB feature sources, a Cassandra feature store, and MinIO/LeoFS (S3) artifact storage. Delivered as a 15-credit research project in the integrated communications systems group (German grade 1.0).

### 5G Testbed - srsRAN and Open5GS, Kubernetes
Built a Kubernetes-based end-to-end 5G testbed (kubeadm) running srsRAN gNB and Open5GS core as pods, with Multus CNI multi-homing (N2/N3/N6) and ZeroMQ virtual RF. Ran host UEs as Docker containers in network namespaces via a macvlan bridge; implemented GTP tunneling and MTU-aware routing with policy-based steering. Integrated an O-RAN SC Near-RT RIC over E2 with Python xApps (E2SM-KPM/RC) and an ONOS SDN controller. Configured comprehensive Prometheus and Grafana monitoring stacks inside the Kubernetes cluster to capture real-time UPF network throughput, pod CPU profiles, and gNB radio metrics; achieved 50+ Mbps TCP throughput.

## Skills

- Languages (spoken): English (fluent), German / Deutsch (A2)
- Telecom & O-RAN: 5G SA, Open5GS (5GC), srsRAN (gNB), O-RAN SC Near-RT RIC, E2 Interface (E2SM-KPM/RC/CCC), ZMQ/UHD, USRP SDR, Multus CNI, SDN (ONOS), GTP Tunneling, macvlan, policy-based routing
- Cloud & Infrastructure: Kubernetes, kustomize, Skaffold, Docker, Helm, Terraform, Cilium, external-dns, AWS (EC2, RDS, DynamoDB, S3)
- Systems & Networking: gRPC, NATS (JetStream + KV), Kafka, Dapr, OpenTelemetry, ZeroMQ, Multus
- Data & ML: Kubeflow Pipelines, KServe, scikit-learn, TensorFlow/Keras, pandas, InfluxDB, MongoDB, Cassandra, pgvector
- Programming: Python, Go, SQL, TypeScript, JavaScript, Bash, PHP
- Web & Frameworks: ReactJS, NodeJS, NestJS, Django
