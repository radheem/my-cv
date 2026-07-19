---
tagline: "Senior Cloud Engineer"
---

## Berufserfahrung

### AiVader GmbH - Research Engineering Intern
Germany | 02/2026 - 04/2026
- Brachte eine containerisierte 5G Standalone platform (Open5GS, RIC, srsRAN) auf einem einzelnen Host betriebsbereit, wodurch die gesamte Bereitstellung vollständig reproduzierbar und mit klaren Runbooks dokumentiert wurde.
- Integrierte xApp über die E2 interface, veröffentlichte gNB telemetry über einen Message Broker für die Echtzeit-SRE metrics reporting.
- Implementierte Observability-Lösungen und behob Engpässe in der Plattform.
- Tech: Kubernetes, Docker, Prometheus, Grafana, InfluxDB, Telegraf, Linux, C++, Bash.

### Al Hilal Invest - Senior Software Engineer
Pakistan | 11/2023 - 03/2024
- Containerisierte Backend-Dienste und optimierte Deployment-Pipelines auf AWS EC2 und Kubernetes, wodurch die Plattformzuverlässigkeit und Release-Geschwindigkeit erhöht wurden.
- Leitete Systemdesigns und Code Reviews, um Architekturstandards für cloud-native Microservices und containerisierte Workloads durchzusetzen.
- Integrierte Anwendungsdienste mit AWS S3, MySQL und MongoDB, um eine skalierbare und produktionsreife Auslieferung zu unterstützen.

### Bluefin Exchange - Senior Software Engineer
Pakistan | 06/2021 - 08/2023
- Integrierte OpenTelemetry distributed tracing, Prometheus metrics und Grafana alerting, um den Durchsatz der Transaction Engine und den Kafka consumer lag zu überwachen, wodurch Latenzspitzen erheblich reduziert wurden.
- Pflegte Release-Prozesse und cloud-native Deployment-Standards für Börsendienste unter Nutzung von Docker und Kubernetes.
- Leitete Engineering-Teams bei Systemdesign-Reviews und Plattformzuverlässigkeitsinitiativen zur Optimierung der Börseninfrastruktur.

## Ausbildung

### Technical University of Ilmenau
Master of Research, Computer Systems and Engineering | 04/2024 - Present

### National University of Computer and Engineering Sciences
Bachelor of Science, Computer Science | 06/2016 - 08/2020

## Projekte

### Homelab (Zero-Touch LAN DNS) ([portfolio](https://radheem.github.io/my-cv/projects/homelab/))
- Entwarf einen **zero-touch service contract**, bei dem ein Entwickler lediglich eine Workload sowie eine `HTTPRoute` mit einem `*.home.lan` hostname definiert — DNS publication und wildcard HTTPS sind vollständig automatisiert.
- Implementierte ein **automatic LAN DNS** mittels **ExternalDNS**, das Gateway API resources überwacht und Einträge in **etcd (`/skydns`)** schreibt, bereitgestellt durch einen **authoritative CoreDNS** conditional forwarder.
- Stellte ein **shared Cilium Gateway** als einzigen HTTP/HTTPS entrypoint auf einer fest zugewiesenen L2 `LoadBalancer` IP bereit, das ein `*.home.lan` wildcard certificate einer **cert-manager internal CA** terminiert.
- Veröffentlichte ein **selectable add-on component registry** mit node-exporter, VictoriaMetrics operator, OpenTelemetry operator, Grafana, NATS und Hatchet, das über einen declarative installer aktiviert/deaktiviert werden kann.

### Information Retrieval System (IRS) - Distributed Systems Platform (Stealth Project) ([portfolio](https://radheem.github.io/my-cv/projects/irs/))
- Migrierte die Plattform von Dapr zu nativem NATS JetStream (messaging), NATS KV (session state) und direktem gRPC, wodurch der Betriebsaufwand und die Latenz reduziert wurden.
- Deployte Go-Microservices mit Kubernetes, kustomize, Skaffold, Cilium und external-dns; integrierte OpenTelemetry distributed tracing und Prometheus metric collection über alle Dienste hinweg.
- Implementierte eine MCP integration, die die Plattform LLM agents als declarative, hot-reloadable tools über einen config-driven toolbox server zugänglich macht.

## Kenntnisse

- Sprachen (gesprochen): Englisch (fließend), Deutsch (A2)
- Cloud & Platform Infra: Kubernetes, Cilium, Docker, Helm, external-dns, Terraform, AWS (EC2, RDS, DynamoDB), kustomize, Skaffold
- Observability & SRE: OpenTelemetry, Prometheus, VictoriaMetrics, Grafana, distributed tracing, metrics, alerting
- Systems & Networking: NATS (JetStream + KV), Kafka, gRPC, Dapr, MCP (FastMCP), ZeroMQ, policy-based routing
- Programmiersprachen: Go, Python, SQL, TypeScript, JavaScript, Bash, PHP
- Databases: PostgreSQL (sqlc), MySQL, MongoDB/DocumentDB, Dgraph, DynamoDB, BigQuery, Snowflake
- ML/Data & Web: Kubeflow Pipelines, KServe, scikit-learn, TensorFlow/Keras, pandas, ReactJS, NodeJS, NestJS, Django
