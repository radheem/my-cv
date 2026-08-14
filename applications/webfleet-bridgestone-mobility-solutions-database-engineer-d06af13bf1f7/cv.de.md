---
tagline: "Database Engineer"
---

## Berufserfahrung

### AiVader GmbH - Research Engineering Intern
Germany | 02/2026 - 04/2026
- Bereitstellung der Datenbank- und Analytics-Stacks für den produktiven Einsatz, Konfiguration des ETL-Prozesses in einen Cassandra Feature Store.
- Integration einer xApp zur Extrahierung von Echtzeit-Funkmetriken über die E2-Schnittstelle und Veröffentlichung über einen Message Broker.
- Aufbau vollständig reproduzierbarer, runbook-konfigurierter Bereitstellungen des containerisierten, datenbankgestützten Stacks (Open5GS, InfluxDB, Cassandra) auf einem einzelnen Linux-Host.
- Tech: InfluxDB, MongoDB, Cassandra, Kafka, Telegraf, PostgreSQL, Python, SQL.

### Al Hilal Invest - Senior Software Engineer
Pakistan | 11/2023 - 03/2024
- Architektur und Dockerisierung von Backend-Services, Leitung von Systemdesign-Reviews zur Optimierung der Datenspeicherung und transaktionaler Workflows über MySQL und MongoDB.
- Entwicklung datengetriebener Features und APIs, Etablierung robuster Dokumentationsstandards für skalierbare Informationsverwaltungssysteme.
- Optimierung von Deployment-Pipelines und Infrastruktur-Bereitstellung auf AWS EC2 und Kubernetes zur Unterstützung hochverfügbarer Daten-Services.

### Bluefin Exchange - Senior Software Engineer
Pakistan | 06/2021 - 08/2023
- Optimierung der Performance der Transaktions-Engine und der Datenspeicherung durch Integration von PostgreSQL und DynamoDB, wodurch Latenzspitzen in hochdurchsatzstarken Börsen-Services direkt reduziert wurden.
- Konzeption und Implementierung umfassender Datenanalyse- und Monitoring-Dashboards mit Grafana, Prometheus und OpenTelemetry zur Überwachung des Transaktionsdurchsatzes und des Kafka Consumer Lag.
- Leitung von Systemdesign-Reviews und Code-Architektur für kritische datenbankgestützte Services, Mentoring von Junior-Entwicklern zu skalierbaren Mustern der Datenspeicherung.

## Ausbildung

### Technical University of Ilmenau
Master of Research, Computer Systems and Engineering | 04/2024 - Present

### National University of Computer and Engineering Sciences
Bachelor of Science, Computer Science | 06/2016 - 08/2020

## Projekte

### My Notebook (Document RAG) ([portfolio](https://radheem.github.io/my-cv/projects/my-notebook/))
- Aufbau eines robusten, wiederholbaren Dokumenten-Ingestion-Pipelines mit Hatchet (extract → chunk → embed → summarize → index), mit Timeout-Konfiguration pro Schritt und absturzsicheren Wiederholungen.
- Implementierung der Vektorsuche mit pgvector (HNSW, cosine) und Echtzeit-Status-Streaming über NATS JetStream + SSE zur persistenten Zustandsverfolgung.
- Cloud-native Bereitstellung auf k3d mit cert-manager TLS und ExternalDNS, wobei alle Inferenzen lokal über zwei llama.cpp-Server hinter einer OpenAI-kompatiblen API ausgeführt werden.

### Information Retrieval System (IRS) - Distributed Systems Platform (Stealth Project) ([portfolio](https://radheem.github.io/my-cv/projects/irs/))
- **Aufbau eines best-effort ETL-Side-Channels** in **PostgreSQL (sqlc)**, **Dgraph** (Graphdatenbank) und **DocumentDB** (NoSQL Cold-Archive), orchestriert von **Hatchet** mit deklarativem Routing.
- **Migration des Session-State und der Messaging-Komponenten** der Plattform von Dapr zu nativen **NATS JetStream (Streaming)** und **NATS KV (Session-State)**, mit direkten gRPC-Verbindungen zur Optimierung der Transaktionslatenz.
- **Integration mehrerer Drittanbieter** über einen Adaptor/Anti-Corruption-Contract mit **CUE-basierter Schema-Mapping**, um die strukturelle Datenintegrität über heterogene Quellen hinweg durchzusetzen.
- **Bereitstellung von Go-Mikroservices** mit **Kubernetes**, **kustomize**, **Skaffold** und **Cilium**, um robustes, isoliertes Routing und hochverfügbare Betriebsabläufe zu gewährleisten.

## Kenntnisse
- Sprachen (gesprochen): Englisch (fließend), Deutsch (A2)
- Datenbanken & Persistenz: PostgreSQL (sqlc), MySQL, MongoDB/DocumentDB, Dgraph, DynamoDB, BigQuery, Snowflake
- Daten & Analytics: pandas, scikit-learn, Kubeflow Pipelines, KServe, Grafana, VictoriaMetrics
- Programmiersprachen: Python, SQL, Go, TypeScript, JavaScript, Bash, PHP
- Systeme & ETL/Streaming: Kafka, NATS (JetStream + KV), Hatchet, MCP (FastMCP), gRPC, Dapr, OpenTelemetry
- Cloud/Infra & Architektur: Kubernetes, kustomize, Skaffold, Cilium, external-dns, Docker, Helm, Terraform, AWS (EC2, RDS, DynamoDB)
- Web: ReactJS, NodeJS, NestJS, Django
