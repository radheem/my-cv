---
tagline: "Studentenpraktikum / Abschlussarbeit / Werkstudent - Cloud-Anwendungen"
---

## Berufserfahrung

### AiVader GmbH - Research Engineering Intern
Germany | 02/2026 - 04/2026
- Überführte eine containerisierte 5G-Standalone-Plattform (Open5GS, RIC, srsRAN) auf einem einzelnen Host in einen betriebsbereiten Zustand, wodurch die gesamte Bereitstellung vollständig reproduzierbar und durch klare Runbooks dokumentiert ist.
- Integrierte die xApp über die E2-Schnittstelle und veröffentlichte gNB-Telemetriedaten an einen Message Broker für die Echtzeit-Metrikenberichterstattung im SRE-Bereich.
- Implementierte Observability-Maßnahmen und behob Engpässe der Plattform.
- Tech: Kubernetes, Docker, Prometheus, Grafana, InfluxDB, Telegraf, Linux, C++, Bash.

### Al Hilal Invest - Senior Software Engineer
Pakistan | 11/2023 - 03/2024
- Containerisierte Backend-Dienste und optimierte Bereitstellungs-Pipelines auf AWS EC2 und Kubernetes, wodurch die Plattformzuverlässigkeit und Release-Geschwindigkeit verbessert wurden.
- Leitete Systemdesigns und Code-Reviews durch, um architektonische Standards für cloud-native Microservices und containerisierte Workloads durchzusetzen.
- Integrierte Anwendungsdienste mit AWS S3, MySQL und MongoDB, um eine skalierbare, produktionsreife Bereitstellung zu unterstützen.

### Bluefin Exchange - Senior Software Engineer
Pakistan | 06/2021 - 08/2023
- Integrierte OpenTelemetry-Distributed-Tracing, Prometheus-Metriken und Grafana-Alerting, um den Durchsatz der Transaktions-Engine und den Kafka-Consumer-Lag zu überwachen, wodurch Latenzspitzen erheblich reduziert wurden.
- Pflegte Release-Prozesse und cloud-native Bereitstellungsstandards für Börsendienste unter Verwendung von Docker und Kubernetes.
- Leitete Engineering-Teams bei Systemdesign-Reviews und Plattformzuverlässigkeitsinitiativen zur Optimierung der Börseninfrastruktur.

## Ausbildung

### Technical University of Ilmenau
Master of Research, Computer Systems and Engineering | 04/2024 - Present

### National University of Computer and Engineering Sciences
Bachelor of Science, Computer Science | 06/2016 - 08/2020

## Projekte

### Homelab (Zero-Touch LAN DNS) ([portfolio](https://radheem.github.io/my-cv/projects/homelab/))
- Entwickelte einen **Zero-Touch-Service-Vertrag**, bei dem ein Entwickler lediglich eine Workload sowie eine `HTTPRoute` mit einem `*.home.lan`-Hostname definiert — die DNS-Veröffentlichung und das Wildcard-HTTPS sind vollständig automatisiert.
- Implementierte ein **automatisches LAN-DNS** mittels **ExternalDNS**, das Gateway-API-Ressourcen überwacht und Einträge in **etcd (`/skydns`)** schreibt, bedient durch einen **autoritativen CoreDNS**-Conditional-Forwarder.
- Stellte ein **freigegebenes Cilium-Gateway** als einzigen HTTP/HTTPS-Eingangspunkt auf einer fest zugewiesenen L2 `LoadBalancer`-IP bereit, das ein `*.home.lan`-Wildcard-Zertifikat terminiert, das von einer **cert-manager-internen CA** ausgestellt wurde.
- Lieferte ein **auswählbares Add-On-Komponenten-Registry**, das node-exporter, VictoriaMetrics Operator, OpenTelemetry Operator, Grafana, NATS und Hatchet umfasst und über einen deklarativen Installer aktiviert oder deaktiviert werden kann.

### Information Retrieval System (IRS) - Distributed Systems Platform (Stealth Project) ([portfolio](https://radheem.github.io/my-cv/projects/irs/))
- Migrierte die Plattform von Dapr auf natives NATS JetStream (Messaging), NATS KV (Sitzungsstatus) und direktes gRPC, wodurch der Betriebsaufwand und die Latenz reduziert wurden.
- Bereitete Go-Microservices mit Kubernetes, kustomize, Skaffold, Cilium und external-dns bereit; integrierte OpenTelemetry-Distributed-Tracing und Prometheus-Metrikerfassung über alle Dienste hinweg.
- Entwickelte eine MCP-Integration, die die Plattform LLM-Agenten als deklarative, hot-reloadable Tools über einen konfigurationsgesteuerten Toolbox-Server verfügbar macht.

## Kenntnisse

- Sprachen (gesprochen): Englisch (fließend), Deutsch (A2)
- Cloud- & Platform-Infra: Kubernetes, Cilium, Docker, Helm, external-dns, Terraform, AWS (EC2, RDS, DynamoDB), kustomize, Skaffold
- Observability & SRE: OpenTelemetry, Prometheus, VictoriaMetrics, Grafana, Distributed Tracing, Metriken, Alerting
- Systems & Networking: NATS (JetStream + KV), Kafka, gRPC, Dapr, MCP (FastMCP), ZeroMQ, policy-based Routing
- Programmiersprachen: Go, Python, SQL, TypeScript, JavaScript, Bash, PHP
- Datenbanken: PostgreSQL (sqlc), MySQL, MongoDB/DocumentDB, Dgraph, DynamoDB, BigQuery, Snowflake
- ML/Data & Web: Kubeflow Pipelines, KServe, scikit-learn, TensorFlow/Keras, pandas, ReactJS, NodeJS, NestJS, Django
