---
tagline: "Senior Cloud Engineer"
---

## Berufserfahrung

### AiVader GmbH / TU Ilmenau (ICS Group) - Research Engineering Intern (5G & Open RAN)
Germany | 02/2026 - 04/2026
- Entwarf eine containerisierte 5G-Standalone-Plattform auf einem einzelnen Host, verwaltete CPU-/Speicherzuweisungen, Ressourcenlimits und Netzwerk-Routing (macvlan/OVS und UPF-Masquerading).
- Integrierte Telegraf, InfluxDB und Grafana, um SRE-Dashboards zu erstellen, die Echtzeit-gNB/UE-Metriken, CPU-Verhungern unter Last und CQI/RSRP-Berichte überwachen.
- Behob niedrigstufige Plattformengpässe, darunter Priority-Thread-Pinning für Echtzeit-SDR-Verarbeitung sowie AVX2/AVX512-SIGILL-Compiling-Fehlanpassungen auf dem Host.
- Tech: Kubernetes, Docker, Prometheus, Grafana, InfluxDB, Telegraf, Linux, C++, Bash.

### Al Hilal Invest - Senior Software Engineer
Pakistan | 11/2023 - 03/2024
- Containerisierte Backend-Dienste und optimierte Deployment-Pipelines auf AWS EC2 und Kubernetes, wodurch die Plattformzuverlässigkeit und Release-Geschwindigkeit gesteigert wurden.
- Leitete Systemdesigns und Code-Reviews durch, um Architekturstandards für cloud-native Microservices und containerisierte Workloads durchzusetzen.
- Integrierte Anwendungsdienste mit AWS S3, MySQL und MongoDB, um eine skalierbare und produktionsreife Auslieferung zu unterstützen.

### Bluefin Exchange - Senior Software Engineer
Pakistan | 06/2021 - 08/2023
- Integrierte OpenTelemetry Distributed Tracing, Prometheus-Metriken und Grafana-Alerting, um den Durchsatz der Transaktions-Engine und den Kafka-Consumer-Lag zu überwachen, wodurch Latenzspitzen erheblich reduziert wurden.
- Wartete Release-Prozesse und cloud-native Deployment-Standards für Börsendienste unter Verwendung von Docker und Kubernetes.
- Leitete Engineering-Teams bei Systemdesign-Reviews und Plattformzuverlässigkeitsinitiativen zur Optimierung der Börseninfrastruktur.

## Ausbildung

### Technical University of Ilmenau
Master of Research, Computer Systems and Engineering | 04/2024 - Present

### National University of Computer and Engineering Sciences
Bachelor of Science, Computer Science | 06/2016 - 08/2020

## Projekte

### Homelab (Zero-Touch LAN DNS) ([portfolio](https://radheem.github.io/my-cv/projects/homelab/))
- Entwarf einen **zero-touch service contract**, bei dem ein Entwickler lediglich ein Workload sowie eine `HTTPRoute` mit einem `*.home.lan`-Hostname definiert — DNS-Publikation und wildcard HTTPS sind vollständig automatisiert.
- Entwickelte **automatisches LAN-DNS** mittels **ExternalDNS**, um Gateway-API-Ressourcen zu überwachen und Einträge in **etcd (`/skydns`)** zu schreiben, bereitgestellt durch einen **authoritativen CoreDNS**-Conditional-Forwarder.
- Stellte ein **shared Cilium Gateway** als einzigen HTTP/HTTPS-Entrypoint auf einer fest zugewiesenen L2 `LoadBalancer`-IP bereit, das ein `*.home.lan`-Wildcard-Zertifikat einer **cert-manager internal CA** terminiert.
- Lieferte ein **selektierbares Add-on-Component-Registry** mit node-exporter, VictoriaMetrics Operator, OpenTelemetry Operator, Grafana, NATS und Hatchet, das über einen deklarativen Installer umschaltbar ist.

### Information Retrieval System (IRS) - Distributed Systems Platform (Stealth Project) ([portfolio](https://radheem.github.io/my-cv/projects/irs/))
- Migrierte die Plattform von Dapr auf natives NATS JetStream (Messaging), NATS KV (Session-State) und direktes gRPC, wodurch der operative Aufwand und die Latenz reduziert wurden.
- Bereitete Go-Microservices mit Kubernetes, kustomize, Skaffold, Cilium und external-dns bereit; integrierte OpenTelemetry Distributed Tracing und Prometheus-Metrik-Sammlung über alle Dienste hinweg.
- Entwickelte eine MCP-Integration, die die Plattform LLM-Agents als deklarative, hot-reloadable Tools über einen konfigurationsgetriebenen Toolbox-Server zugänglich machte.

## Kenntnisse

- Sprachen (gesprochen): Englisch (fließend), Deutsch (A2)
- Cloud & Platform Infra: Kubernetes, Cilium, Docker, Helm, external-dns, Terraform, AWS (EC2, RDS, DynamoDB), kustomize, Skaffold
- Observability & SRE: OpenTelemetry, Prometheus, VictoriaMetrics, Grafana, Distributed Tracing, Metriken, Alerting
- Systems & Networking: NATS (JetStream + KV), Kafka, gRPC, Dapr, MCP (FastMCP), ZeroMQ, policy-based Routing
- Programmiersprachen: Go, Python, SQL, TypeScript, JavaScript, Bash, PHP
- Datenbanken: PostgreSQL (sqlc), MySQL, MongoDB/DocumentDB, Dgraph, DynamoDB, BigQuery, Snowflake
- ML/Data & Web: Kubeflow Pipelines, KServe, scikit-learn, TensorFlow/Keras, pandas, ReactJS, NodeJS, NestJS, Django
