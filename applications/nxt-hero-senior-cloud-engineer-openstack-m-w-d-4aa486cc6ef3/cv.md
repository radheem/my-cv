---
tagline: "Senior Cloud Engineer"
---

## Experience

### AiVader GmbH / TU Ilmenau (ICS Group) - Research Engineering Intern (5G & Open RAN)
Germany | 02/2026 - 04/2026
- Brought a containerized 5G Standalone platform (Open5GS, RIC, srsRAN) to operational readiness on a single host, making the entire deployment fully reproducible with clear runbooks.
- Integrated a custom xApp over the E2 interface, publishing gNB telemetry to a Kafka pub-sub cluster for real-time SRE metrics reporting.
- Built comprehensive observability (Telegraf -> InfluxDB -> Grafana) and resolved platform bottlenecks, including priority thread pinning for real-time SDR processing and host-level AVX2 compilation crashes.
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

### Homelab (Zero-Touch LAN DNS) ([portfolio](https://radheem.github.io/my-cv/projects/homelab/))
- Designed a **zero-touch service contract** where a workload plus an `HTTPRoute` with a `*.home.lan` hostname is all a developer writes — DNS publication and wildcard HTTPS are fully automatic.
- Built **automatic LAN DNS** using **ExternalDNS** to watch Gateway API resources and write records to **etcd (`/skydns`)**, served by an **authoritative CoreDNS** conditional forwarder.
- Delivered a **shared Cilium Gateway** as the single HTTP/HTTPS entrypoint on a pinned L2 `LoadBalancer` IP, terminating a `*.home.lan` wildcard certificate issued by a **cert-manager internal CA**.
- Shipped a **selectable add-on component registry** including node-exporter, VictoriaMetrics operator, OpenTelemetry operator, Grafana, NATS, and Hatchet, toggleable from a declarative installer.

### Information Retrieval System (IRS) - Distributed Systems Platform (Stealth Project) ([portfolio](https://radheem.github.io/my-cv/projects/irs/))
- Migrated the platform off Dapr to native NATS JetStream (messaging), NATS KV (session state), and direct gRPC, reducing operational overhead and latency.
- Deployed Go microservices with Kubernetes, kustomize, Skaffold, Cilium, and external-dns; integrated OpenTelemetry distributed tracing and Prometheus metric collection across all services.
- Built an MCP integration exposing the platform to LLM agents as declarative, hot-reloadable tools via a config-driven toolbox server.

## Skills

- Languages (spoken): English (fluent), German / Deutsch (A2)
- Cloud & Platform Infra: Kubernetes, Cilium, Docker, Helm, external-dns, Terraform, AWS (EC2, RDS, DynamoDB), kustomize, Skaffold
- Observability & SRE: OpenTelemetry, Prometheus, VictoriaMetrics, Grafana, distributed tracing, metrics, alerting
- Systems & Networking: NATS (JetStream + KV), Kafka, gRPC, Dapr, MCP (FastMCP), ZeroMQ, policy-based routing
- Programming Languages: Go, Python, SQL, TypeScript, JavaScript, Bash, PHP
- Databases: PostgreSQL (sqlc), MySQL, MongoDB/DocumentDB, Dgraph, DynamoDB, BigQuery, Snowflake
- ML/Data & Web: Kubeflow Pipelines, KServe, scikit-learn, TensorFlow/Keras, pandas, ReactJS, NodeJS, NestJS, Django
