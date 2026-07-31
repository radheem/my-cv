---
tagline: "Data Engineer Windenergie"
---

## Berufserfahrung

### AiVader GmbH - Research Engineering Intern
Germany | 02/2026 - 04/2026
- Brachte den Datenbank- und Analytik-Stack in einen betriebsbereiten Zustand, konfigurierte ETL-Pipelines für einen Cassandra Feature Store.
- Integrierte eine xApp, die Echtzeit-Funkmetriken über die E2-Schnittstelle extrahiert und diese an einen Message Broker veröffentlicht.
- Implementierte vollständig reproduzierbare, nach Runbook konfigurierte Deployments des containerisierten, datenbankgestützten Stacks (Open5GS, InfluxDB, Cassandra) auf einem einzelnen Linux-Host.
- Tech: InfluxDB, MongoDB, Cassandra, Kafka, Telegraf, PostgreSQL, Python, SQL.

### Al Hilal Invest - Senior Software Engineer
Pakistan | 11/2023 - 03/2024
- Architekturierte und containerisierte Backend-Dienste (Docker), leitete Systemdesign-Reviews zur Optimierung der Datenpersistenz und transaktionaler Workflows über MySQL und MongoDB hinweg.
- Entwickelte neue datengetriebene Features und APIs, etablierte robuste Dokumentationsstandards für skalierbare Informationsmanagementsysteme.
- Optimierte Deployment-Pipelines und Infrastruktur-Bereitstellung auf AWS EC2 und Kubernetes zur Unterstützung hochverfügbarer Daten Dienste.

### Bluefin Exchange - Senior Software Engineer
Pakistan | 06/2021 - 08/2023
- Optimierte die Performance der Transaktions-Engine und die Datenpersistenz durch die Integration von PostgreSQL und DynamoDB, wodurch Latenzspitzen in durchsatzstarken Börsendiensten direkt reduziert wurden.
- Konzipierte und implementierte umfassende Dashboards für Datenanalyse und Monitoring mit Grafana, Prometheus und OpenTelemetry zur Verfolgung des Transaktionsdurchsatzes und des Kafka Consumer Lag.
- Leitete Systemdesign-Reviews und Code-Architektur-Reviews für kritische datenbankgestützte Dienste, betreute und mentorierte Junior-Entwickler zu skalierbaren Mustern der Datenpersistenz.

## Ausbildung

### Technical University of Ilmenau
Master of Research, Computer Systems and Engineering | 04/2024 - Present

### National University of Computer and Engineering Sciences
Bachelor of Science, Computer Science | 06/2016 - 08/2020

## Projekte

### My Notebook (Document RAG) ([portfolio](https://radheem.github.io/my-cv/projects/my-notebook/))
- Entwickelte eine robuste, wiederholbare Dokumenten-Ingestion-Pipeline mit Hatchet (extract → chunk → embed → summarize → index) mit Timeout-Einstellungen pro Schritt und crashresistenten Wiederholungen.
- Implementierte Vektorsuche mit pgvector (HNSW, cosine) und Echtzeit-Fortschritts-Streaming über NATS JetStream + SSE für die persistente Statusverfolgung.
- Bereitgestellt als Cloud-Native-Anwendung auf k3d mit cert-manager TLS und ExternalDNS, wobei alle Inferenzen lokal über zwei llama.cpp-Server hinter einer OpenAI-kompatiblen API erfolgen.

### Information Retrieval System (IRS) - Distributed Systems Platform (Stealth Project) ([portfolio](https://radheem.github.io/my-cv/projects/irs/))
- **Implementierte einen best-effort ETL-Sidechannel** in **PostgreSQL (sqlc)**, **Dgraph** (Graphdatenbank) und **DocumentDB** (NoSQL Cold-Archive), orchestriert von **Hatchet** mit deklarativem Routing.
- **Migrierte den Session-State und die Messaging-Komponenten der Plattform** von Dapr zu nativen **NATS JetStream (Streaming)** und **NATS KV (Session-State)**, mit direkten gRPC-Verbindungen zur Optimierung der Transaktionslatenz.
- **Integrierte mehrere Drittanbieter** über einen Adapter-/Anti-Corruption-Vertrag mit **CUE-basierter Schema-Mapping**, um die strukturelle Datenintegrität über heterogene Quellen hinweg sicherzustellen.
- **Stellte Go-Mikrodienste bereit** mit **Kubernetes**, **kustomize**, **Skaffold** und **Cilium**, um robustes, isoliertes Routing und hochverfügbare Betriebsabläufe zu gewährleisten.

## Kenntnisse

- Sprachen (gesprochen): Englisch (fließend), Deutsch (A2)
- Datenbanken & Persistenz: PostgreSQL (sqlc), MySQL, MongoDB/DocumentDB, Dgraph, DynamoDB, BigQuery, Snowflake
- Daten & Analytik: pandas, scikit-learn, Kubeflow Pipelines, KServe, Grafana, VictoriaMetrics
- Programmiersprachen: Python, SQL, Go, TypeScript, JavaScript, Bash, PHP
- Systeme & ETL/Streaming: Kafka, NATS (JetStream + KV), Hatchet, MCP (FastMCP), gRPC, Dapr, OpenTelemetry
- Cloud/Infra & Architektur: Kubernetes, kustomize, Skaffold, Cilium, external-dns, Docker, Helm, Terraform, AWS (EC2, RDS, DynamoDB)
- Web: ReactJS, NodeJS, NestJS, Django
