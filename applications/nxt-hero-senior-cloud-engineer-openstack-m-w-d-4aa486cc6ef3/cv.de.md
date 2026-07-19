---
tagline: "Senior Cloud Engineer"
---

## Berufserfahrung

### AiVader GmbH / TU Ilmenau (ICS Group) - Research Engineering Intern (5G & Open RAN)
Germany | 02/2026 - 04/2026
- Brachte eine containerisierte 5G-Standalone-Plattform (Open5GS, RIC, srsRAN) auf einen produktionsreifen Zustand auf einem einzelnen Host, wodurch die gesamte Bereitstellung vollständig reproduzierbar und mit klaren Runbooks dokumentiert wurde.
- Integrierte die xApp über die E2-Schnittstelle und veröffentlichte gNB-Telemetriedaten im Message Broker für Echtzeit-SRE-Metrikenberichte.
- Implementierte Observability-Lösungen und behob Engpässe in der Plattform.
- Tech: Kubernetes, Docker, Prometheus, Grafana, InfluxDB, Telegraf, Linux, C++, Bash.

### Al Hilal Invest - Senior Software Engineer
Pakistan | 11/2023 - 03/2024
- Containerisierte Backend-Dienste und optimierte Deployment-Pipelines auf AWS EC2 und Kubernetes, wodurch die Plattformzuverlässigkeit und Release-Geschwindigkeit erhöht wurden.
- Leitete Systemdesigns und Code-Reviews zur Durchsetzung architektonischer Standards für cloud-native Microservices und containerisierte Workloads.
- Integrierte Anwendungsdienste mit AWS S3, MySQL und MongoDB, um skalierbare, produktionsreife Bereitstellungen zu unterstützen.

### Bluefin Exchange - Senior Software Engineer
Pakistan | 06/2021 - 08/2023
- Integrierte OpenTelemetry-Distributed-Tracing, Prometheus-Metriken und Grafana-Alerting zur Überwachung der Transaktions-Engine-Durchsatzrate und des Kafka-Consumer-Lags, wodurch Latenzspitzen signifikant reduziert wurden.
- Pflegte Release-Prozesse und cloud-native Deployment-Standards für Börsendienste unter Verwendung von Docker und Kubernetes.
- Leitete Engineering-Teams bei Systemdesign-Reviews und Plattformzuverlässigkeitsinitiativen zur Optimierung der Börseninfrastruktur.

## Ausbildung

### Technical University of Ilmenau
Master of Research, Computer Systems and Engineering | 04/2024 - Present

### National University of Computer and Engineering Sciences
Bachelor of Science, Computer Science | 06/2016 - 08/2020

## Projekte

### Homelab (Zero-Touch LAN DNS) ([portfolio](https://radheem.github.io/my-cv/projects/homelab/))
- Entwarf einen **Zero-Touch-Service-Contract**, bei dem ein Entwickler lediglich ein Workload sowie eine `HTTPRoute` mit einem `*.home.lan`-Hostname definiert — DNS-Publikation und Wildcard-HTTPS sind vollständig automatisiert.
- Implementierte ein **automatisches LAN-DNS** mittels **ExternalDNS**, das Gateway-API-Ressourcen überwacht und Einträge in **etcd (`/skydns`)** schreibt, bereitgestellt durch einen **autoritativen CoreDNS**-Conditional-Forwarder.
- Stellte ein **freigegebenes Cilium Gateway** als einzigen HTTP/HTTPS-Eingangspunkt auf einer fest zugewiesenen L2 `LoadBalancer`-IP bereit, das ein `*.home.lan`-Wildcard-Zertifikat einer **cert-manager-Internen CA** terminiert.
- Veröffentlichte ein **auswählbares Add-On-Komponentenregister** mit node-exporter, VictoriaMetrics Operator, OpenTelemetry Operator, Grafana, NATS und Hatchet, das über einen deklarativen Installer aktiviert/deaktiviert werden kann.

### Information Retrieval System (IRS) - Distributed Systems Platform (Stealth Project) ([portfolio](https://radheem.github.io/my-cv/projects/irs/))
- Migrierte die Plattform von Dapr zu nativem NATS JetStream (Messaging), NATS KV (Session-State) und direktem gRPC, wodurch der Betriebsaufwand und die Latenz reduziert wurden.
- Stellte Go-Microservices mit Kubernetes, kustomize, Skaffold, Cilium und external-dns bereit; integrierte OpenTelemetry-Distributed-Tracing und Prometheus-Metriksammlung über alle Dienste hinweg.
- Entwickelte eine MCP-Integration, die die Plattform LLM-Agenten als deklarativen, hot-reloadable Tools über einen konfigurationsgesteuerten Toolbox-Server zugänglich macht.

## Kenntnisse

- Sprachen (gesprochen): Englisch (fließend), Deutsch (A2)
- Cloud- & Plattform-Infrastruktur: Kubernetes, Cilium, Docker, Helm, external-dns, Terraform, AWS (EC2, RDS, DynamoDB), kustomize, Skaffold
- Observability & SRE: OpenTelemetry, Prometheus, VictoriaMetrics, Grafana, Distributed Tracing, Metriken, Alerting
- Systeme & Netzwerktechnik: NATS (JetStream + KV), Kafka, gRPC, Dapr, MCP (FastMCP), ZeroMQ, policy-based Routing
- Programmiersprachen: Go, Python, SQL, TypeScript, JavaScript, Bash, PHP
- Datenbanken: PostgreSQL (sqlc), MySQL, MongoDB/DocumentDB, Dgraph, DynamoDB, BigQuery, Snowflake
- ML/Daten & Web: Kubeflow Pipelines, KServe, scikit-learn, TensorFlow/Keras, pandas, ReactJS, NodeJS, NestJS, Django
