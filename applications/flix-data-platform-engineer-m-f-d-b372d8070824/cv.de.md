---
tagline: "Data Platform Engineer"
---

## Berufserfahrung

### AiVader GmbH - Research Engineering Intern
Germany | 02/2026 - 04/2026
- Brachte eine containerisierte 5G-Standalone-Plattform (Open5GS, RIC, srsRAN) auf einem einzelnen Host in den produktionsreifen Zustand und machte die gesamte Bereitstellung vollständig reproduzierbar mit klaren Runbooks.
- Integrierte xApp über die E2-Schnittstelle und veröffentlichte gNB-Telemetriedaten über einen Message Broker für die Echtzeit-Metrikenberichterstattung im SRE-Bereich.
- Implementierte Observability und behob Engpässe in der Plattform.
- Tech: Kubernetes, Docker, Prometheus, Grafana, InfluxDB, Telegraf, Linux, C++, Bash.

### Al Hilal Invest - Senior Software Engineer
Pakistan | 11/2023 - 03/2024
- Containerisierte Backend-Dienste und optimierte Deployment-Pipelines auf AWS EC2 und Kubernetes, wodurch die Plattformzuverlässigkeit und Release-Geschwindigkeit erhöht wurden.
- Leitete Systemdesign und Code Reviews zur Durchsetzung architektonischer Standards für cloud-native Microservices und containerisierte Workloads.
- Integrierte Anwendungsdienste mit AWS S3, MySQL und MongoDB, um eine skalierbare, produktionsreife Auslieferung zu unterstützen.

### Bluefin Exchange - Senior Software Engineer
Pakistan | 06/2021 - 08/2023
- Integrierte OpenTelemetry Distributed Tracing, Prometheus-Metriken und Grafana-Alerting zur Überwachung des Transaction-Engine-Durchsatzes und des Kafka Consumer Lag, wodurch Latenzspitzen erheblich reduziert wurden.
- Pflegte Release-Prozesse und cloud-native Deployment-Standards für alle Börsendienste unter Verwendung von Docker und Kubernetes.
- Leitete Engineering-Teams bei Systemdesign-Reviews und Plattformzuverlässigkeitsinitiativen zur Optimierung der Börseninfrastruktur.

## Ausbildung

### Technical University of Ilmenau
Master of Research, Computer Systems and Engineering | 04/2024 - Present

### National University of Computer and Engineering Sciences
Bachelor of Science, Computer Science | 06/2016 - 08/2020

## Projekte

### O-RAN Testbed (Open5GS + RIC + OCUDU gNB)
- Architettierte eine hochperformante Kafka-Metriken-Pub/Sub-Pipeline, bei der xApps pro-UE-KPM-Daten an Kafka veröffentlichen, wobei Consumer die Daten an InfluxDB 3/Grafana, MongoDB und eine AIMLFW-kompatible InfluxDB 2 für Echtzeit-Analysen und Speicherung weiterleiten.
- Entwickelte kompositionsfähige Docker Compose-Stacks zur Orchestrierung der Open5GS-, RIC- und OCUDU gNB-Komponenten, was schnelle, reproduzierbare Testbed-Bereitstellungen und optimierte Integrationsworkflows ermöglichte.

### My Notebook (Document RAG)
- Implementierte eine robuste, wiederholbare Dokumenten-Ingestion-Pipeline mit Hatchet, die Extract → Chunk → Embed → Summarize → Index-Workflows orchestriert, mit granularer Schritt-für-Schritt-Timeout-Konfiguration und automatischen Wiederholungen zur Garantie einer fehlerresistenten Datenverarbeitung.
- Implementierte Echtzeit-Fortschritts-Streaming über NATS JetStream und Server-Sent Events (SSE), das transparente Pipeline-Telemetrie bereitstellt und sofortiges Feedback für langlaufende RAG-Indexierungsvorgänge ermöglicht.

## Kenntnisse

- **Sprachen & Kernkompetenzen:** Python, Go, SQL, TypeScript, JavaScript, Bash, PHP, Englisch (fließend), Deutsch (A2)
- **Systeme & Infrastruktur:** Kubernetes, Terraform, AWS (EC2, RDS, DynamoDB, S3), Docker, Helm, kustomize, Skaffold, GitLab CI/CD, event-driven architecture, Streaming, ETL/ELT-Pipelines, Data Engineering, Monitoring & Observability (Prometheus, Grafana, OpenTelemetry)
- **Datenbanken & Data Engineering:** Snowflake, BigQuery, PostgreSQL (sqlc), MySQL, MongoDB, Dgraph, Kafka, NATS (JetStream + KV), gRPC, Kubeflow Pipelines, KServe, scikit-learn, TensorFlow/Keras, pandas, ReactJS, NodeJS, NestJS, Django
