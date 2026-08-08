---
tagline: "Werkstudent in der Abteilung Robotik"
---

## Berufserfahrung

### AiVader GmbH - Research Engineering Intern
Germany | 02/2026 - 04/2026
- Brachte eine containerisierte 5G-Standalone-Plattform (Open5GS, RIC, srsRAN) auf einem einzelnen Host in einen betriebsbereiten Zustand und machte die gesamte Bereitstellung vollständig reproduzierbar mit klaren Runbooks.
- Integrierte xApp über die E2-Schnittstelle und veröffentlichte gNB-Telemetriedaten über einen Message Broker für Echtzeit-SRE-Metrikenberichte.
- Implementierung von Observability-Lösungen und Behebung von Plattformengpässen.
- Tech: Kubernetes, Docker, Prometheus, Grafana, InfluxDB, Telegraf, Linux, C++, Bash.

### Al Hilal Invest - Senior Software Engineer
Pakistan | 11/2023 - 03/2024
- Containerisierung von Backend-Diensten und Optimierung von Deployment-Pipelines auf AWS EC2 und Kubernetes, zur Verbesserung der Plattformzuverlässigkeit und Release-Geschwindigkeit.
- Leitung von Systemdesigns und Code-Reviews zur Durchsetzung architektonischer Standards für cloud-native Microservices und containerisierte Workloads.
- Integration von Anwendungsdiensten mit AWS S3, MySQL und MongoDB zur Unterstützung skalierbarer, produktionsreifer Bereitstellungen.

### Bluefin Exchange - Senior Software Engineer
Pakistan | 06/2021 - 08/2023
- Integration von OpenTelemetry Distributed Tracing, Prometheus-Metriken und Grafana-Alerting zur Überwachung der Durchsatzleistung der Transaktions-Engine und des Kafka Consumer Lag, wodurch Latenzspitzen erheblich reduziert wurden.
- Pflege von Release-Prozessen und cloud-nativen Bereitstellungsstandards für Börsendienste unter Verwendung von Docker und Kubernetes.
- Leitung von Engineering-Teams bei Systemdesign-Reviews und Plattformzuverlässigkeitsinitiativen zur Optimierung der Börseninfrastruktur.

## Ausbildung

### Technical University of Ilmenau
Master of Research, Computer Systems and Engineering | 04/2024 - Present

### National University of Computer and Engineering Sciences
Bachelor of Science, Computer Science | 06/2016 - 08/2020

## Projekte

### Homelab (Zero-Touch LAN DNS) ([portfolio](https://radheem.github.io/my-cv/projects/homelab/))
- Entwickelte einen **Zero-Touch-Service-Vertrag**, bei dem ein Entwickler lediglich eine Workload sowie eine `HTTPRoute` mit einem `*.home.lan`-Hostnamen definiert — DNS-Publikation und Wildcard-HTTPS sind vollständig automatisiert.
- Aufbau eines **automatischen LAN-DNS** mittels **ExternalDNS** zur Überwachung von Gateway-API-Ressourcen und zum Schreiben von Einträgen in **etcd (`/skydns`)**, bedient durch einen **authoritativen CoreDNS**-Conditional-Forwarder.
- Bereitstellung eines **shared Cilium Gateways** als einziger HTTP/HTTPS-Eingangspunkt auf einer fest zugewiesenen L2 `LoadBalancer`-IP, der ein `*.home.lan`-Wildcard-Zertifikat terminiert, das von einer **cert-manager-internalen CA** ausgestellt wurde.
- Auslieferung eines **auswählbaren Add-On-Komponenten-Registries** einschließlich node-exporter, VictoriaMetrics Operator, OpenTelemetry Operator, Grafana, NATS und Hatchet, das über einen deklarativen Installer umschaltbar ist.

### Information Retrieval System (IRS) - Distributed Systems Platform (Stealth Project) ([portfolio](https://radheem.github.io/my-cv/projects/irs/))
- Migration der Plattform von Dapr zu nativem NATS JetStream (Messaging), NATS KV (Session-State) und direktem gRPC, wodurch operativer Aufwand und Latenz reduziert wurden.
- Bereitstellung von Go-Microservices mit Kubernetes, kustomize, Skaffold, Cilium und external-dns; Integration von OpenTelemetry Distributed Tracing und Prometheus-Metrikerfassung über alle Dienste hinweg.
- Entwicklung einer MCP-Integration, die die Plattform LLM-Agents als deklarative, hot-reloadable Tools über einen konfigurationsgetriebenen Toolbox-Server zugänglich macht.

## Kenntnisse

- Sprachen (gesprochen): Englisch (fließend), Deutsch (A2)
- Cloud- & Platform-Infra: Kubernetes, Cilium, Docker, Helm, external-dns, Terraform, AWS (EC2, RDS, DynamoDB), kustomize, Skaffold
- Observability & SRE: OpenTelemetry, Prometheus, VictoriaMetrics, Grafana, distributed tracing, metrics, alerting
- Systems & Networking: NATS (JetStream + KV), Kafka, gRPC, Dapr, MCP (FastMCP), ZeroMQ, policy-based routing
- Programmiersprachen: Go, Python, SQL, TypeScript, JavaScript, Bash, PHP
- Datenbanken: PostgreSQL (sqlc), MySQL, MongoDB/DocumentDB, Dgraph, DynamoDB, BigQuery, Snowflake
- ML/Data & Web: Kubeflow Pipelines, KServe, scikit-learn, TensorFlow/Keras, pandas, ReactJS, NodeJS, NestJS, Django
