---
tagline: "Student Software Developer Backend & Data Processing"
---

## Berufserfahrung

### Al Hilal Invest - Senior Software Engineer
Pakistan | 11/2023 - 03/2024
- Backend-Dienste entworfen und in Docker containerisiert, Systemdesign-Reviews geleitet zur Optimierung der Datenpersistenz und transaktionaler Workflows über MySQL und MongoDB hinweg.
- Neue datengetriebene Features und APIs entwickelt, robuste Dokumentationsstandards für skalierbare Informationsmanagementsysteme etabliert.
- Deployment-Pipelines und Infrastruktur-Bereitstellung auf AWS EC2 und Kubernetes optimiert, um hochverfügbare Daten-Dienste zu unterstützen.

### Bluefin Exchange - Senior Software Engineer
Pakistan | 06/2021 - 08/2023
- Performance der Transaktions-Engine und Datenpersistenz durch Integration von PostgreSQL und DynamoDB optimiert, wodurch Latenzspitzen in durchsatzstarken Börsen-Diensten direkt reduziert wurden.
- Umfassende Dashboards für Datenanalyse und Monitoring mit Grafana, Prometheus und OpenTelemetry entworfen und implementiert, um Transaktionsdurchsatz und Kafka-Consumer-Lag zu verfolgen.
- Systemdesign-Reviews und Code-Architektur für kritische datenbankgestützte Dienste geleitet, Junior-Engineers bei skalierbaren Datenpersistenzmustern betreut.

### Seed Labs - Software Engineer
Pakistan | 06/2020 - 06/2021
- Daten-ETL-Pipelines und analytische Workflows mit Python und SQL entwickelt, Rohdatensätze für Stakeholder-Berichte bereinigt und transformiert.
- Datenvisualisierungs-Charts und Insights-Dashboards zur Darstellung analytischer Erkenntnisse entwickelt, MySQL und MongoDB für persistente Datenspeicherung genutzt.

## Ausbildung

### Technical University of Ilmenau
Master of Research, Computer Systems and Engineering | 04/2024 - Present

### National University of Computer and Engineering Sciences
Bachelor of Science, Computer Science | 06/2016 - 08/2020

## Projekte

### My Notebook (Document RAG) ([portfolio](https://radheem.github.io/my-cv/projects/my-notebook/))
- Robuste, wiederholbare Document-Ingestion-Pipeline mit Hatchet (extract → chunk → embed → summarize → index) aufgebaut, mit Timeout-Konfiguration pro Schritt und absturzsicheren Wiederholungen.
- Vektorsuche mit pgvector (HNSW, cosine) und Echtzeit-Fortschritts-Streaming über NATS JetStream + SSE für persistente Statusverfolgung implementiert.
- Cloud-nativ auf k3d mit cert-manager TLS und ExternalDNS bereitgestellt, alle Inferences lokal über zwei llama.cpp-Server hinter einer OpenAI-kompatiblen API gehalten.

### cv-tailor (LLM CV/Cover Tailoring + LinkedIn Automation) ([portfolio](https://radheem.github.io/my-cv/projects/cv-tailor/))
- Python-CLI und **FastMCP Server** entwickelt, die CV/Anschreiben-Anpassung automatisieren, mit unit-getesteter Projekt-Ranking (Anthropic/Ollama) und Halluzinations-Schutz.
- Automatisierte **Gmail alert ingestion**-Pipeline und leichtgewichtiges Guest-API-Fetching entwickelt, integriert mit bidirektionaler **Google Sheets synchronization** für Lifecycle-Tracking.
- Sensible Dokumente in Git mittels clientseitiger **AES-256-GCM**-Verschlüsselung gesichert, hinter passwortgeschützten statischen Pages geschützt.

## Kenntnisse

- Sprachen (gesprochen): Englisch (fließend), Deutsch (A2)
- Datenbanken & Persistenz: PostgreSQL (sqlc), MySQL, MongoDB/DocumentDB, Dgraph, DynamoDB, BigQuery, Snowflake
- Daten & Analytik: pandas, scikit-learn, Kubeflow Pipelines, KServe, Grafana, VictoriaMetrics
- Programmiersprachen: Python, SQL, Go, TypeScript, JavaScript, Bash, PHP
- Systeme & ETL/Streaming: Kafka, NATS (JetStream + KV), Hatchet, MCP (FastMCP), gRPC, Dapr, OpenTelemetry
- Cloud/Infra & Architektur: Kubernetes, kustomize, Skaffold, Cilium, external-dns, Docker, Helm, Terraform, AWS (EC2, RDS, DynamoDB)
- Web: ReactJS, NodeJS, NestJS, Django
