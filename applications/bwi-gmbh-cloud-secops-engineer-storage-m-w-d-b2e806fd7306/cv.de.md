---
tagline: "Storage Platform Engineer (Private Cloud)"
---

## Berufserfahrung

### AiVader GmbH - Research Engineering Intern
Germany | 02/2026 - 04/2026
- Brachte eine containerisierte 5G-Standalone-Plattform (Open5GS, RIC, srsRAN) auf einen einzelnen Host in einen betriebsbereiten Zustand und machte die gesamte Bereitstellung durch klare Runbooks vollständig reproduzierbar.
- Integrierte xApp über die E2-Schnittstelle und veröffentlichte gNB-Telemetriedaten im Message Broker für Echtzeit-SRE-Metrikenberichte.
- Implementierte Observability und behob Engpässe in der Plattform.
- Tech: Kubernetes, Docker, Prometheus, Grafana, InfluxDB, Telegraf, Linux, C++, Bash.

### Al Hilal Invest - Senior Software Engineer
Pakistan | 11/2023 - 03/2024
- Containerisierte Backend-Dienste und optimierte Deployment-Pipelines auf AWS EC2 und Kubernetes, wodurch die Plattformzuverlässigkeit und Release-Geschwindigkeit erhöht wurden.
- Leitete Systemdesigns und Code-Reviews, um architektonische Standards für cloud-native Microservices und containerisierte Workloads durchzusetzen.
- Integrierte Anwendungsdienste mit AWS S3, MySQL und MongoDB, um eine skalierbare, produktionsreife Auslieferung zu unterstützen.

### Bluefin Exchange - Senior Software Engineer
Pakistan | 06/2021 - 08/2023
- Integrierte OpenTelemetry Distributed Tracing, Prometheus-Metriken und Grafana-Alerting, um den Durchsatz der Transaktions-Engine und den Kafka Consumer Lag zu überwachen, was Latenzspitzen erheblich reduzierte.
- Pflegte Release-Prozesse und cloud-native Deployment-Standards für Börsendienste unter Verwendung von Docker und Kubernetes.
- Leitete Engineering-Teams bei Systemdesign-Reviews und Plattformzuverlässigkeitsinitiativen zur Optimierung der Börseninfrastruktur.

## Ausbildung

### Technical University of Ilmenau
Master of Research, Computer Systems and Engineering | 04/2024 - Present

### National University of Computer and Engineering Sciences
Bachelor of Science, Computer Science | 06/2016 - 08/2020

## Projekte

### Homelab (Zero-Touch LAN DNS) ([portfolio](https://radheem.github.io/my-cv/projects/homelab/))
- Entwarf einen **zero-touch service contract**, bei dem ein Entwickler nur ein Workload plus eine `HTTPRoute` mit einem `*.home.lan`-Hostname schreiben muss — die DNS-Veröffentlichung und das Wildcard-HTTPS sind vollständig automatisiert.
- Implementierte **automatisches LAN-DNS** mit **ExternalDNS**, um Gateway-API-Ressourcen zu überwachen und Einträge in **etcd (`/skydns`)** zu schreiben, bereitgestellt durch einen **authoritativen CoreDNS**-Conditional-Forwarder.
- Stellte ein **shared Cilium Gateway** als einzigen HTTP/HTTPS-Eingangspunkt auf einer festen L2 `LoadBalancer`-IP bereit, das ein `*.home.lan`-Wildcard-Zertifikat terminiert, das von einer **cert-manager internal CA** ausgestellt wurde.
- Stellte ein **auswählbares Add-on-Komponenten-Registry** bereit, das node-exporter, VictoriaMetrics Operator, OpenTelemetry Operator, Grafana, NATS und Hatchet umfasst und über einen deklarativen Installer umschaltbar ist.

### Information Retrieval System (IRS) - Distributed Systems Platform (Stealth Project) ([portfolio](https://radheem.github.io/my-cv/projects/irs/))
- Migrierte die Plattform von Dapr zu nativem NATS JetStream (Messaging), NATS KV (Session-State) und direktem gRPC, wodurch der Betriebsaufwand und die Latenz reduziert wurden.
- Stellte Go-Microservices mit Kubernetes, kustomize, Skaffold, Cilium und external-dns bereit; integrierte OpenTelemetry Distributed Tracing und Prometheus-Metriksammlung über alle Dienste hinweg.
- Implementierte eine MCP-Integration, die die Plattform als deklarative, hot-reloadable Tools über einen konfigurationsgetriebenen Toolbox-Server für LLM-Agents verfügbar macht.

## Kenntnisse

- Sprachen (gesprochen): Englisch (fließend), Deutsch (A2)
- Cloud- & Plattform-Infrastruktur: Kubernetes, k3d, Cilium, Docker, Helm, external-dns, Terraform, AWS (EC2, RDS, DynamoDB), kustomize, Skaffold, Keycloak
- Observability & SRE: OpenTelemetry, Prometheus, VictoriaMetrics, Grafana, Distributed Tracing, Metriken, Alerting
- Systeme & Netzwerk: NATS (JetStream + KV), Kafka, gRPC, Dapr, MCP (FastMCP), ZeroMQ, policy-based routing
- Programmiersprachen: Go, Python, SQL, TypeScript, JavaScript, Bash, PHP
- Datenbanken: PostgreSQL (sqlc), MySQL, MongoDB/DocumentDB, Dgraph, DynamoDB, BigQuery, Snowflake
- ML/Daten & Web: Kubeflow Pipelines, KServe, scikit-learn, TensorFlow/Keras, pandas, ReactJS, NodeJS, NestJS, Django
