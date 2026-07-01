---
tagline: "Fullstack Engineer (Data Focus)"
---

## Berufserfahrung

### Al Hilal Invest - Senior Software Engineer
Pakistan | 11/2023 - 03/2024
- Backend-Dienste entworfen und in Docker containerisiert, Systemdesign-Reviews geleitet zur Optimierung der Datenpersistenz und transaktionaler Workflows über MySQL und MongoDB.
- Neue datengetriebene Features und APIs entwickelt, robuste Dokumentationsstandards für skalierbare Informationsmanagementsysteme etabliert.
- Deployment-Pipelines und Infrastruktur-Bereitstellung auf AWS EC2 und Kubernetes optimiert, um hochverfügbare Daten-Dienste zu unterstützen.

### Bluefin Exchange - Senior Software Engineer
Pakistan | 06/2021 - 08/2023
- Performance der Transaktions-Engine und Datenpersistenz durch Integration von PostgreSQL und DynamoDB optimiert, wodurch Latenzspitzen in hochdurchsatzstarken Börsen-Diensten direkt reduziert wurden.
- Umfassende Dashboards für Datenanalyse und Monitoring mit Grafana, Prometheus und OpenTelemetry entworfen und implementiert, um Transaktionsdurchsatz und Kafka-Consumer-Lag zu verfolgen.
- Systemdesign-Reviews und Code-Architektur für kritische, datenbankgestützte Dienste geleitet; Junior-Engineers bei skalierbaren Mustern der Datenpersistenz betreut.

### Seed Labs - Software Engineer
Pakistan | 06/2020 - 06/2021
- Daten-ETL-Pipelines und analytische Workflows mit Python und SQL entwickelt, Rohdatensätze für Stakeholder-Berichte bereinigt und transformiert.
- Datenvisualisierungen und Insights-Dashboards zur Darstellung analytischer Ergebnisse entwickelt, wobei MySQL und MongoDB für die persistente Datenspeicherung genutzt wurden.

## Ausbildung

### Technical University of Ilmenau
Master of Research, Computer Systems and Engineering | 04/2024 - Heute

### National University of Computer and Engineering Sciences
Bachelor of Science, Computer Science | 06/2016 - 08/2020

## Projekte

### Second Brain (Document RAG) ([repo](https://github.com/radheem/my-notebook))
- Robuste, wiederholbare Dokumenten-Ingestion-Pipeline mit Hatchet (extract → chunk → embed → summarize → index) aufgebaut, mit Timeout-Konfiguration pro Schritt und absturzsicheren Wiederholungen.
- Vektorsuche mit pgvector (HNSW, cosine) implementiert sowie Echtzeit-Fortschritts-Streaming über NATS JetStream + SSE für persistente Statusverfolgung umgesetzt.
- Cloud-native auf k3d mit cert-manager TLS und ExternalDNS bereitgestellt, wobei alle Inferenzen lokal über zwei llama.cpp-Server hinter einer OpenAI-kompatiblen API gehalten wurden.

### cv-tailor (LLM CV/Cover Tailoring + LinkedIn Automation) ([repo](https://github.com/radheem/cv-tailor))
- Python-CLI und **FastMCP Server** entwickelt, die die Anpassung von Lebenslauf und Anschreiben automatisieren, mit unit-getesteter Projekt-Ranking-Funktion (Anthropic/Ollama) und Halluzinations-Filtern.
- Automatisierte **Gmail-Alert-Ingestion**-Pipeline und leichtgewichtige Guest-API-Abfrage entwickelt, integriert mit bidirektionaler **Google Sheets-Synchronisation** zur Lebenszyklus-Verfolgung.
- Sensible Dokumente in Git mittels clientseitiger **AES-256-GCM**-Verschlüsselung gesichert, geschützt durch passwortgeschützte statische Pages.

## Kenntnisse

- Sprachen (gesprochen): Englisch (fließend), Deutsch (A2)
- Databases & Persistence: PostgreSQL (sqlc), MySQL, MongoDB/DocumentDB, Dgraph, DynamoDB, BigQuery, Snowflake
- Data & Analytics: pandas, scikit-learn, Kubeflow Pipelines, KServe, Grafana, VictoriaMetrics
- Programmiersprachen: Python, SQL, Go, TypeScript, JavaScript, Bash, PHP
- Systems & ETL/Streaming: Kafka, NATS (JetStream + KV), Hatchet, MCP (FastMCP), gRPC, Dapr, OpenTelemetry
- Cloud/Infra & Architecture: Kubernetes, kustomize, Skaffold, Cilium, external-dns, Docker, Helm, Terraform, AWS (EC2, RDS, DynamoDB)
- Web: ReactJS, NodeJS, NestJS, Django
