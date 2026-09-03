---
tagline: "Data Engineer – Erfüllungs- & Logistikdaten"
---

## Berufserfahrung

### AiVader GmbH - Research Engineering Intern
Germany | 02/2026 - 04/2026
- Stellte den Datenbank- und Analytik-Stack betriebsbereit, indem ein ETL-Prozess in einen Cassandra Feature Store konfiguriert wurde.
- Integrierte eine xApp, die Echtzeit-Funkmetriken über die E2-Schnittstelle extrahiert und diese an einen Message Broker veröffentlicht.
- Implementierte vollständig reproduzierbare, runbook-konfigurierte Deployments des containerisierten, datenbankgestützten Stacks (Open5GS, InfluxDB, Cassandra) auf einem einzelnen Linux-Host.
- Technologien: InfluxDB, MongoDB, Cassandra, Kafka, Telegraf, PostgreSQL, Python, SQL.

### Al Hilal Invest - Senior Software Engineer
Pakistan | 11/2023 - 03/2024
- Architekturierte und containerisierte (Docker) Backend-Dienste, leitete Systemdesign-Reviews zur Optimierung der Datenpersistenz und transaktionaler Workflows über MySQL und MongoDB hinweg.
- Entwickelte neue datengetriebene Features und APIs, etablierte robuste Dokumentationsstandards für skalierbare Informationsverwaltungssysteme.
- Optimierte Deployment-Pipelines und Infrastruktur-Bereitstellung auf AWS EC2 und Kubernetes zur Unterstützung hochverfügbarer Daten-Dienste.

### Bluefin Exchange - Senior Software Engineer
Pakistan | 06/2021 - 08/2023
- Optimierte die Leistung der Transaktions-Engine und die Datenpersistenz durch die Integration von PostgreSQL und DynamoDB, wodurch Latenzspitzen in hochdurchsatzstarken Börsendiensten direkt reduziert wurden.
- Entwarf und implementierte umfassende Dashboards für Datenanalyse und Monitoring mit Grafana, Prometheus und OpenTelemetry zur Verfolgung des Transaktionsdurchsatzes und des Kafka Consumer Lag.
- Leitete Systemdesign-Reviews und Code-Architektur für kritische, datenbankgestützte Dienste, mentorierte Junior-Entwickler in skalierbaren Mustern der Datenpersistenz.

## Ausbildung

### Technical University of Ilmenau
Master of Research, Computer Systems and Engineering | 04/2024 - Present

### National University of Computer and Engineering Sciences
Bachelor of Science, Computer Science | 06/2016 - 08/2020

## Projekte

### My Notebook (Document RAG) ([portfolio](https://radheem.github.io/my-cv/projects/my-notebook/))
- Entwickelte eine robuste, wiederholbare Dokumenten-Ingestion-Pipeline mit Hatchet (extract → chunk → embed → summarize → index) mit Timeout-Einstellungen pro Schritt und absturzsicheren Wiederholungen.
- Implementierte Vektorsuche mit pgvector (HNSW, cosine) und Echtzeit-Fortschritts-Streaming über NATS JetStream + SSE zur persistenten Statusverfolgung.
- Bereitgestellt als cloud-native Anwendung auf k3d mit cert-manager TLS und ExternalDNS, wobei alle Inferenzen lokal über zwei llama.cpp-Server hinter einer OpenAI-kompatiblen API gehalten wurden.

### Information Retrieval System (IRS) - Distributed Systems Platform (Stealth Project) ([portfolio](https://radheem.github.io/my-cv/projects/irs/))
- **Implementierte einen best-effort ETL-Sidechannel** in **PostgreSQL (sqlc)**, **Dgraph** (Graphdatenbank) und **DocumentDB** (NoSQL Cold-Archive), orchestriert durch **Hatchet** mit deklarativem Routing.
- **Migrierte den Sitzungsstatus und die Nachrichtenübermittlung der Plattform** von Dapr auf natives **NATS JetStream (Streaming)** und **NATS KV (Sitzungsstatus)** mit direkten gRPC-Verbindungen zur Optimierung der Transaktionslatenz.
- **Integrierte mehrere Drittanbieter** über einen Adaptor/Anti-Corruption-Contract mit **CUE-basierter Schema-Mapping**, um die strukturelle Datenintegrität über heterogene Quellen hinweg sicherzustellen.
- **Bereitgestellt Go-Mikrodienste** mit **Kubernetes**, **kustomize**, **Skaffold** und **Cilium**, um robustes, isoliertes Routing und hochverfügbare Betriebsabläufe zu gewährleisten.

## Kenntnisse

- Sprachen (gesprochen): Englisch (fließend), Deutsch (A2)
- Datenbanken & Persistenz: PostgreSQL (sqlc), MySQL, MongoDB/DocumentDB, Dgraph, DynamoDB, BigQuery, Snowflake
- Daten & Analytik: pandas, scikit-learn, Kubeflow Pipelines, KServe, Grafana, VictoriaMetrics
- Programmiersprachen: Python, SQL, Go, TypeScript, JavaScript, Bash, PHP
- Systeme & ETL/Streaming: Kafka, NATS (JetStream + KV), Hatchet, MCP (FastMCP), gRPC, Dapr, OpenTelemetry
- Cloud/Infra & Architektur: Kubernetes, kustomize, Skaffold, Cilium, external-dns, Docker, Helm, Terraform, AWS (EC2, RDS, DynamoDB)
- Web: ReactJS, NodeJS, NestJS, Django
