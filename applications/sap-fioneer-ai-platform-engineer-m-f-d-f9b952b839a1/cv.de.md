---
tagline: "AI Platform Engineer"
---

## Berufserfahrung

### AiVader GmbH - Research Engineering Intern
Germany | 02/2026 - 04/2026
- Containerisierte 5G-Standalone-Plattform (Open5GS, RIC, srsRAN) auf einem einzelnen Host betriebsbereit gemacht, wodurch die gesamte Bereitstellung mit klaren Runbooks vollständig reproduzierbar wurde.
- Integrierte xApp über die E2-Schnittstelle und veröffentlichte gNB-Telemetriedaten über den Message Broker für die Echtzeit-Berichterstattung von SRE-Metriken.
- Aufbau von Observability-Funktionalitäten und Beseitigung von Engpässen in der Plattform.
- Tech: Kubernetes, Docker, Prometheus, Grafana, InfluxDB, Telegraf, Linux, C++, Bash.

### Al Hilal Invest - Senior Software Engineer
Pakistan | 11/2023 - 03/2024
- Containerisierte Backend-Dienste und optimierte Deployment-Pipelines auf AWS EC2 und Kubernetes, wodurch die Plattformzuverlässigkeit und Release-Geschwindigkeit erhöht wurden.
- Leitete Systemdesigns und Code-Reviews zur Durchsetzung architektonischer Standards für cloud-native Microservices und containerisierte Workloads.
- Integrierte Anwendungsdienste mit AWS S3, MySQL und MongoDB zur Unterstützung einer skalierbaren, produktionsreifen Bereitstellung.

### Bluefin Exchange - Senior Software Engineer
Pakistan | 06/2021 - 08/2023
- Integrierte OpenTelemetry-Distributed-Tracing, Prometheus-Metriken und Grafana-Alerting zur Überwachung des Durchsatzes der Transaktions-Engine und des Kafka-Consumer-Lag, wodurch Latenzspitzen erheblich reduziert wurden.
- Pflegte Release-Prozesse und cloud-native Deployment-Standards für Börsendienste unter Nutzung von Docker und Kubernetes.
- Leitete Engineering-Teams bei Systemdesign-Reviews und Plattformzuverlässigkeitsinitiativen zur Optimierung der Börseninfrastruktur.

## Ausbildung

### Technical University of Ilmenau
Master of Research, Computer Systems and Engineering | 04/2024 - Present

### National University of Computer and Engineering Sciences
Bachelor of Science, Computer Science | 06/2016 - 08/2020

## Projekte

### Homelab (Zero-Touch LAN DNS) ([portfolio](https://radheem.github.io/my-cv/projects/homelab/))
- Entwickelte einen **zero-touch service contract**, bei dem ein Entwickler lediglich ein Workload sowie eine `HTTPRoute` mit einem `*.home.lan`-Hostname definiert — die DNS-Veröffentlichung und das wildcard HTTPS sind vollständig automatisiert.
- Entwickelte **automatisches LAN-DNS** mittels **ExternalDNS** zur Überwachung von Gateway-API-Ressourcen und zum Schreiben von Einträgen in **etcd (`/skydns`)**, bedient durch einen **authoritativen CoreDNS**-Conditional-Forwarder.
- Bereitgestellt ein **shared Cilium Gateway** als einzigen HTTP/HTTPS-Eingangspunkt auf einer festen L2 `LoadBalancer`-IP, der ein `*.home.lan`-Wildcard-Zertifikat terminiert, das von einer **cert-manager-internal CA** ausgestellt wurde.
- Entwickelt ein **auswählbares Add-On-Komponenten-Registry** mit node-exporter, VictoriaMetrics Operator, OpenTelemetry Operator, Grafana, NATS und Hatchet, das über einen deklarativen Installer aktiviert werden kann.

### Information Retrieval System (IRS) - Distributed Systems Platform (Stealth Project) ([portfolio](https://radheem.github.io/my-cv/projects/irs/))
- Migrierte die Plattform von Dapr zu nativem NATS JetStream (Messaging), NATS KV (Session-State) und direktem gRPC, wodurch der Betriebsaufwand und die Latenz reduziert wurden.
- Bereitgestellt Go-Microservices mit Kubernetes, kustomize, Skaffold, Cilium und external-dns; OpenTelemetry-Distributed-Tracing und Prometheus-Metriksammlung über alle Dienste hinweg integriert.
- Entwickelt eine MCP-Integration, die die Plattform LLM-Agenten als deklarative, hot-reloadable Tools über einen konfigurationsgesteuerten Toolbox-Server zugänglich macht.

## Kenntnisse

- Sprachen (gesprochen): Englisch (fließend), Deutsch (A2)
- Cloud & Platform Infra: Kubernetes, Cilium, Docker, Helm, external-dns, Terraform, AWS (EC2, RDS, DynamoDB), kustomize, Skaffold
- Observability & SRE: OpenTelemetry, Prometheus, VictoriaMetrics, Grafana, distributed tracing, metrics, alerting
- Systems & Networking: NATS (JetStream + KV), Kafka, gRPC, Dapr, MCP (FastMCP), ZeroMQ, policy-based routing
- Programmiersprachen: Go, Python, SQL, TypeScript, JavaScript, Bash, PHP
- Datenbanken: PostgreSQL (sqlc), MySQL, MongoDB/DocumentDB, Dgraph, DynamoDB, BigQuery, Snowflake
- ML/Data & Web: Kubeflow Pipelines, KServe, scikit-learn, TensorFlow/Keras, pandas, ReactJS, NodeJS, NestJS, Django
