---
tagline: "Database/Platform Engineer"
---

## Berufserfahrung

### AiVader GmbH - Research Engineering Intern
Germany | 02/2026 - 04/2026
- Brachte eine containerisierte 5G-Standalone-Plattform (Open5GS, RIC, srsRAN) auf einem einzelnen Host in Betriebsbereitschaft und machte die gesamte Bereitstellung mit klaren Runbooks vollständig reproduzierbar.
- Integrierte xApp über die E2-Schnittstelle und veröffentlichte gNB-Telemetriedaten über einen Message Broker für die Echtzeit-Metrikenberichterstattung des SRE.
- Implementierte Observability-Lösungen und behob Engpässe der Plattform.
- Tech: Kubernetes, Docker, Prometheus, Grafana, InfluxDB, Telegraf, Linux, C++, Bash.

### Al Hilal Invest - Senior Software Engineer
Pakistan | 11/2023 - 03/2024
- Containerisierte Backend-Dienste und optimierte Bereitstellungspipelines auf AWS EC2 und Kubernetes, wodurch die Plattformzuverlässigkeit und Release-Geschwindigkeit erhöht wurden.
- Leitete Systemdesigns und Code-Reviews durch, um Architekturstandards für cloud-native Microservices und containerisierte Workloads durchzusetzen.
- Integrierte Anwendungsdienste mit AWS S3, MySQL und MongoDB, um eine skalierbare und produktionsreife Auslieferung zu unterstützen.

### Bluefin Exchange - Senior Software Engineer
Pakistan | 06/2021 - 08/2023
- Integrierte OpenTelemetry-Distributed-Tracing, Prometheus-Metriken und Grafana-Alerting, um den Durchsatz der Transaktions-Engine und den Kafka-Consumer-Lag zu überwachen, wodurch Latenzspitzen erheblich reduziert wurden.
- Wartete Release-Prozesse und cloud-native Bereitstellungsstandards für Börsendienste unter Verwendung von Docker und Kubernetes.
- Leitete Engineering-Teams bei Systemdesign-Reviews und Plattformzuverlässigkeitsinitiativen zur Optimierung der Börseninfrastruktur.

## Ausbildung

### Technical University of Ilmenau
Master of Research, Computer Systems and Engineering | 04/2024 - Present

### National University of Computer and Engineering Sciences
Bachelor of Science, Computer Science | 06/2016 - 08/2020

## Projekte

### Homelab (Zero-Touch LAN DNS) ([portfolio](https://radheem.github.io/my-cv/projects/homelab/))
- Entwickelte einen **Zero-Touch-Service-Vertrag**, bei dem ein Entwickler lediglich eine Workload sowie eine `HTTPRoute` mit einem `*.home.lan`-Hostname definiert — DNS-Veröffentlichung und Wildcard-HTTPS sind vollständig automatisiert.
- Implementierte ein **automatisches LAN-DNS** mit **ExternalDNS**, um Gateway-API-Ressourcen zu überwachen und Einträge in **etcd (`/skydns`)** zu schreiben, bedient durch einen **autoritativen CoreDNS**-Conditional-Forwarder.
- Stellte ein **gemeinsames Cilium-Gateway** als einzigen HTTP/HTTPS-Eingangspunkt auf einer fest zugewiesenen L2 `LoadBalancer`-IP bereit, das ein `*.home.lan`-Wildcard-Zertifikat einer **cert-manager-internen CA** terminiert.
- Lieferte ein **auswählbares Add-On-Komponenten-Register** mit node-exporter, VictoriaMetrics-Operator, OpenTelemetry-Operator, Grafana, NATS und Hatchet, das über einen deklarativen Installer aktiviert/deaktiviert werden kann.

### Information Retrieval System (IRS) - Distributed Systems Platform (Stealth Project) ([portfolio](https://radheem.github.io/my-cv/projects/irs/))
- Migrierte die Plattform von Dapr auf natives NATS JetStream (Messaging), NATS KV (Session-State) und direktes gRPC, wodurch der Betriebsaufwand und die Latenz reduziert wurden.
- Bereitete Go-Microservices mit Kubernetes, kustomize, Skaffold, Cilium und external-dns bereit; integrierte OpenTelemetry-Distributed-Tracing und Prometheus-Metrik-Sammlung über alle Dienste hinweg.
- Entwickelte eine MCP-Integration, die die Plattform LLM-Agents als deklarative, hot-reloadable Tools über einen konfigurationsgesteuerten Toolbox-Server zugänglich macht.

## Kenntnisse

- Sprachen (gesprochen): Englisch (fließend), Deutsch (A2)
- Cloud- & Plattform-Infrastruktur: Kubernetes, k3d, Cilium, Docker, Helm, external-dns, Terraform, AWS (EC2, RDS, DynamoDB), kustomize, Skaffold, Keycloak
- Observability & SRE: OpenTelemetry, Prometheus, VictoriaMetrics, Grafana, Distributed Tracing, Metriken, Alerting
- Systeme & Netzwerk: NATS (JetStream + KV), Kafka, gRPC, Dapr, MCP (FastMCP), ZeroMQ, policy-based Routing
- Programmiersprachen: Go, Python, SQL, TypeScript, JavaScript, Bash, PHP
- Datenbanken: PostgreSQL (sqlc), MySQL, MongoDB/DocumentDB, Dgraph, DynamoDB, BigQuery, Snowflake
- ML/Daten & Web: Kubeflow Pipelines, KServe, scikit-learn, TensorFlow/Keras, pandas, ReactJS, NodeJS, NestJS, Django
