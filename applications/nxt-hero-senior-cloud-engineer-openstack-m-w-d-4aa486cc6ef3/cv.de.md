---
tagline: "Senior Cloud Engineer"
---

## Berufserfahrung

### AiVader GmbH / TU Ilmenau (ICS Group) - Research Engineering Intern (5G & Open RAN)
Germany | 02/2026 - 04/2026
- Implementierte eine containerisierte 5G-Standalone-Plattform (Open5GS, RIC, srsRAN) auf einem einzelnen Host, wodurch die gesamte Bereitstellung vollständig reproduzierbar und durch klare Runbooks dokumentiert wurde.
- Integrierte eine benutzerdefinierte xApp über die E2-Schnittstelle und publizierte gNB-Telemetriedaten in einem Kafka-Pub-Sub-Cluster für Echtzeit-Berichte zu SRE-Metriken.
- Aufbau einer Observability-Infrastruktur (Telegraf/Grafana) und Behebung von Plattformengpässen wie Thread-Pinning sowie AVX2-Kompilierungsabstürzen.
- Tech: Kubernetes, Docker, Prometheus, Grafana, InfluxDB, Telegraf, Linux, C++, Bash.

### Al Hilal Invest - Senior Software Engineer
Pakistan | 11/2023 - 03/2024
- Containerisierung von Backend-Diensten und Optimierung von Bereitstellungs-Pipelines auf AWS EC2 und Kubernetes, was die Plattformzuverlässigkeit und Release-Geschwindigkeit steigerte.
- Leitung von Systemdesigns und Code-Reviews zur Durchsetzung von Architekturstandards für cloud-native Microservices und containerisierte Workloads.
- Integration von Anwendungsdiensten mit AWS S3, MySQL und MongoDB zur Unterstützung skalierbarer, produktionsreifer Bereitstellungen.

### Bluefin Exchange - Senior Software Engineer
Pakistan | 06/2021 - 08/2023
- Integration von OpenTelemetry-Distributed-Tracing, Prometheus-Metriken und Grafana-Alerting zur Überwachung des Durchsatzes der Transaktions-Engine sowie des Kafka-Consumer-Lags, wodurch Latenzspitzen erheblich reduziert wurden.
- Aufrechterhaltung von Release-Prozessen und cloud-nativen Bereitstellungsstandards für Exchange-Dienste unter Einsatz von Docker und Kubernetes.
- Leitung von Engineering-Teams bei Systemdesign-Reviews und Initiativen zur Plattformzuverlässigkeit zur Optimierung der Exchange-Infrastruktur.

## Ausbildung

### Technical University of Ilmenau
Master of Research, Computer Systems and Engineering | 04/2024 - Present

### National University of Computer and Engineering Sciences
Bachelor of Science, Computer Science | 06/2016 - 08/2020

## Projekte

### Homelab (Zero-Touch LAN DNS) ([portfolio](https://radheem.github.io/my-cv/projects/homelab/))
- Entwicklung eines **Zero-Touch-Service-Vertrags**, bei dem ein Entwickler lediglich eine Workload sowie eine `HTTPRoute` mit einem `*.home.lan`-Hostnamen implementiert — die DNS-Publikation und Wildcard-HTTPS erfolgen vollständig automatisch.
- Aufbau eines **automatischen LAN-DNS** mit **ExternalDNS** zur Überwachung von Gateway-API-Ressourcen und zum Schreiben von Einträgen in **etcd (`/skydns`)**, bereitgestellt durch einen **authoritativen CoreDNS**-Conditional-Forwarder.
- Bereitstellung eines **gemeinsamen Cilium Gateways** als einzigen HTTP/HTTPS-Eingangspunkt auf einer festen L2 `LoadBalancer`-IP, welches ein von einer **cert-manager-internen CA** ausgestelltes `*.home.lan`-Wildcard-Zertifikat terminiert.
- Implementierung eines **auswählbaren Add-On-Komponenten-Registers** mit node-exporter, VictoriaMetrics Operator, OpenTelemetry Operator, Grafana, NATS und Hatchet, das über einen deklarativen Installer aktiviert oder deaktiviert werden kann.

### Information Retrieval System (IRS) - Distributed Systems Platform (Stealth Project) ([portfolio](https://radheem.github.io/my-cv/projects/irs/))
- Migration der Plattform von Dapr zu nativem NATS JetStream (Messaging), NATS KV (Session-State) und direktem gRPC, wodurch Betriebsaufwand und Latenz signifikant reduziert wurden.
- Bereitstellung von Go-Microservices mit Kubernetes, kustomize, Skaffold, Cilium und external-dns; Integration von OpenTelemetry-Distributed-Tracing und Prometheus-Metrik-Sammlung über alle Dienste hinweg.
- Entwicklung einer MCP-Integration zur Offenlegung der Plattform für LLM-Agenten als deklarative, hot-reloadable Tools über einen konfigurationsgetriebenen Toolbox-Server.

## Kenntnisse
- Sprachen (gesprochen): Englisch (fließend), Deutsch (A2)
- Cloud & Platform Infra: Kubernetes, Cilium, Docker, Helm, external-dns, Terraform, AWS (EC2, RDS, DynamoDB), kustomize, Skaffold
- Observability & SRE: OpenTelemetry, Prometheus, VictoriaMetrics, Grafana, distributed tracing, metrics, alerting
- Systems & Networking: NATS (JetStream + KV), Kafka, gRPC, Dapr, MCP (FastMCP), ZeroMQ, policy-based routing
- Programmiersprachen: Go, Python, SQL, TypeScript, JavaScript, Bash, PHP
- Databases: PostgreSQL (sqlc), MySQL, MongoDB/DocumentDB, Dgraph, DynamoDB, BigQuery, Snowflake
- ML/Data & Web: Kubeflow Pipelines, KServe, scikit-learn, TensorFlow/Keras, pandas, ReactJS, NodeJS, NestJS, Django
