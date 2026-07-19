---
tagline: "Senior Cloud Engineer"
---

## Berufserfahrung

### AiVader GmbH / TU Ilmenau (ICS Group) - Research Engineering Intern (5G & Open RAN)
Germany | 02/2026 - 04/2026
- Machte eine containerisierte 5G-Standalone-Plattform (Open5GS, RIC, srsRAN) auf einem einzelnen Host betriebsbereit und stellte sicher, dass die gesamte Bereitstellung vollständig reproduzierbar ist, unterstützt durch klare Runbooks.
- Integrierte eine benutzerdefinierte xApp über die E2-Schnittstelle und veröffentlichte gNB-Telemetriedaten in einem Kafka-Pub-Sub-Cluster für Echtzeit-SRE-Metrikenberichte.
- Implementierte umfassende Observability (Telegraf -> InfluxDB -> Grafana) und behob Plattformengpässe, einschließlich Priority-Thread-Pinning für Echtzeit-SDR-Verarbeitung und Host-ebene AVX2-Kompilierungsabstürze.
- Tech: Kubernetes, Docker, Prometheus, Grafana, InfluxDB, Telegraf, Linux, C++, Bash.

### Al Hilal Invest - Senior Software Engineer
Pakistan | 11/2023 - 03/2024
- Containerisierte Backend-Dienste und optimierte Deployment-Pipelines auf AWS EC2 und Kubernetes, wodurch die Plattformzuverlässigkeit und Release-Geschwindigkeit erhöht wurden.
- Leitete Systemdesigns und Code-Reviews, um architektonische Standards für cloud-native Microservices und containerisierte Workloads durchzusetzen.
- Integrierte Anwendungsdienste mit AWS S3, MySQL und MongoDB, um eine skalierbare und produktionsreife Auslieferung zu unterstützen.

### Bluefin Exchange - Senior Software Engineer
Pakistan | 06/2021 - 08/2023
- Integrierte OpenTelemetry-Distributed-Tracing, Prometheus-Metriken und Grafana-Alerting, um den Durchsatz der Transaktions-Engine und den Kafka-Consumer-Lag zu überwachen, wodurch Latenzspitzen erheblich reduziert wurden.
- Pflegte Release-Prozesse und cloud-native Deployment-Standards für Börsendienste unter Verwendung von Docker und Kubernetes.
- Leitete Engineering-Teams bei Systemdesign-Reviews und Plattformzuverlässigkeitsinitiativen zur Optimierung der Börseninfrastruktur.

## Ausbildung

### Technical University of Ilmenau
Master of Research, Computer Systems and Engineering | 04/2024 - Present

### National University of Computer and Engineering Sciences
Bachelor of Science, Computer Science | 06/2016 - 08/2020

## Projekte

### Homelab (Zero-Touch LAN DNS) ([portfolio](https://radheem.github.io/my-cv/projects/homelab/))
- Entwarf einen **Zero-Touch-Service-Vertrag**, bei dem ein Entwickler lediglich eine Workload sowie eine `HTTPRoute` mit einem `*.home.lan`-Hostname definiert — DNS-Publikation und Wildcard-HTTPS sind vollständig automatisiert.
- Implementierte **automatisches LAN-DNS** mittels **ExternalDNS**, um Gateway-API-Ressourcen zu überwachen und Einträge in **etcd (`/skydns`)** zu schreiben, bereitgestellt durch einen **autoritativen CoreDNS**-Conditional-Forwarder.
- Stellte ein **shared Cilium Gateway** als einzigen HTTP/HTTPS-Eingangspunkt auf einer fest zugewiesenen L2 `LoadBalancer`-IP bereit, das ein `*.home.lan`-Wildcard-Zertifikat einer **cert-manager-internal-CA** terminiert.
- Veröffentlichte ein **auswählbares Add-On-Komponenten-Registry**, das node-exporter, VictoriaMetrics Operator, OpenTelemetry Operator, Grafana, NATS und Hatchet umfasst, welches über einen deklarativen Installer aktiviert werden kann.

### Information Retrieval System (IRS) - Distributed Systems Platform (Stealth Project) ([portfolio](https://radheem.github.io/my-cv/projects/irs/))
- Migrierte die Plattform von Dapr zu nativem NATS JetStream (Messaging), NATS KV (Session-State) und direktem gRPC, wodurch der Betriebsaufwand und die Latenz reduziert wurden.
- Stellte Go-Microservices mit Kubernetes, kustomize, Skaffold, Cilium und external-dns bereit; integrierte OpenTelemetry Distributed Tracing und Prometheus-Metriksammlung über alle Dienste hinweg.
- Implementierte eine MCP-Integration, die die Plattform LLM-Agenten als deklarative, hot-reloadable Tools über einen konfigurationsgetriebenen Toolbox-Server zugänglich macht.

## Kenntnisse

- Sprachen (gesprochen): Englisch (fließend), Deutsch (A2)
- Cloud & Platform Infra: Kubernetes, Cilium, Docker, Helm, external-dns, Terraform, AWS (EC2, RDS, DynamoDB), kustomize, Skaffold
- Observability & SRE: OpenTelemetry, Prometheus, VictoriaMetrics, Grafana, distributed tracing, metrics, alerting
- Systems & Networking: NATS (JetStream + KV), Kafka, gRPC, Dapr, MCP (FastMCP), ZeroMQ, policy-based routing
- Programmiersprachen: Go, Python, SQL, TypeScript, JavaScript, Bash, PHP
- Databases: PostgreSQL (sqlc), MySQL, MongoDB/DocumentDB, Dgraph, DynamoDB, BigQuery, Snowflake
- ML/Data & Web: Kubeflow Pipelines, KServe, scikit-learn, TensorFlow/Keras, pandas, ReactJS, NodeJS, NestJS, Django
