---
tagline: "Senior O-RAN & Telecommunications Software Engineer"
---

## Experience

### AiVader GmbH - Research Engineering Intern
Germany | 02/2026 - 04/2026
- Integrated and deployed a reproducible 5G Standalone (SA) Open RAN testbed, combining pre-dockerized Open5GS 5GC, O-RAN SC RIC, and srsRAN/OCUDU gNB components.
- Developed and integrated KPM xApp to extract real-time performance metrics over the E2 interface, fanning them out to a message broker.
- Brought both ZeroMQ virtual RF and USRP B210 physical SDR RF pipelines to operational readiness, validating communication.
- Tech: Open5GS, srsRAN/OCUDU, O-RAN SC near-RT RIC, USRP B210, UHD, ZeroMQ, E2SM-KPM.

### Al Hilal Invest - Senior Software Engineer
Pakistan | 11/2023 - 03/2024
- Led system design and code reviews while dockerizing backend services to standardize deployment workflows on Kubernetes and AWS EC2.
- Developed and documented new microservices and features using NodeJS, TypeScript, and PHP, integrating with MySQL and MongoDB.
- Streamlined deployment processes and infrastructure configurations to improve service reliability and release velocity.

### Bluefin Exchange - Senior Software Engineer
Pakistan | 06/2021 - 08/2023
- Integrated Prometheus logging, OpenTelemetry metrics, and Grafana alerts to monitor transaction engine throughput and Kafka consumer group lag, reducing latency spikes.
- Identified system design improvements and proposed independent solutions while reviewing code and architecture as a senior system expert.
- Maintained release processes and documentation for core exchange services while mentoring junior engineers on project initiatives.

## Education

### Technical University of Ilmenau
Master of Research, Computer Systems and Engineering | 04/2024 - Present

### National University of Computer and Engineering Sciences
Bachelor of Science, Computer Science | 06/2016 - 08/2020

## Projects

### O-RAN Testbed (Open5GS + RIC + OCUDU gNB) ([portfolio](https://radheem.github.io/my-cv/projects/oran-testbed/))
- Consolidated a single-host 5G SA testbed into composable Docker Compose stacks (core, gNB ZMQ/UHD, RIC, monitoring, pub/sub) where the 5GC and Near-RT RIC publish host ports so any number of gNBs - local or remote - can attach over shared bridge networks.
- Ran the gNB on the open-source OCUDU CU/DU (srsRAN heritage), building one image for both ZMQ virtual RF and UHD over-the-air on a USRP B210 SDR.
- Integrated the O-RAN SC Near-RT RIC over E2 with Python xApps using E2SM-KPM, E2SM-RC (incl. handover), and E2SM-CCC.

### O-RAN AIML Framework ([portfolio](https://radheem.github.io/my-cv/projects/oran-aiml/))
- Deployed the end-to-end AIML framework on Kubernetes with Helm (training manager, model management, KF adapter, data-extraction, KServe).
- Config-driven Python client/SDK automating the full ML lifecycle: feature group → model → pipeline → training job → inference.
- Delivered as a 15-credit research project; German grade 1.0 (A).

## Skills

- Languages (spoken): English (fluent), Deutsch (A2)
- Cloud/Infra: Kubernetes, kustomize, Skaffold, Cilium, external-dns, Docker, Helm, Terraform, AWS (EC2, RDS, DynamoDB)
- Systems: gRPC, NATS (JetStream + KV), Hatchet, MCP (FastMCP), Kafka, Dapr, OpenTelemetry, VictoriaMetrics, Grafana
- ML/Data: Kubeflow Pipelines, KServe, scikit-learn, TensorFlow/Keras, pandas
- Databases: PostgreSQL (sqlc), MySQL, MongoDB/DocumentDB, Dgraph, DynamoDB, BigQuery, Snowflake
- Web: ReactJS, NodeJS, NestJS, Django
- Programming Languages: Go, Python, SQL, TypeScript, JavaScript, Bash, PHP
