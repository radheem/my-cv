---
tagline: "Cloud Native Data Engineer"
---

## Berufserfahrung

### Al Hilal Invest - Senior Software Engineer
Pakistan | 11/2023 - 03/2024
- Architekturierte und dockerisierte Backend-Dienste, leitete Systemdesign-Reviews zur Optimierung der Datenpersistenz und transaktionaler Workflows über MySQL und MongoDB hinweg.
- Entwickelte neue datengetriebene Features und APIs, etablierte robuste Dokumentationsstandards für skalierbare Informationsmanagementsysteme.
- Optimierte Deployment-Pipelines und Infrastruktur-Bereitstellung auf AWS EC2 und Kubernetes zur Unterstützung hochverfügbarer Daten-Dienste.

### Bluefin Exchange - Senior Software Engineer
Pakistan | 06/2021 - 08/2023
- Optimierte die Performance der Transaktions-Engine und Datenpersistenz durch Integration von PostgreSQL und DynamoDB, wodurch Latenzspitzen in hochdurchsatzstarken Börsen-Diensten direkt reduziert wurden.
- Entwarf und implementierte umfassende Dashboards für Datenanalyse und Monitoring mit Grafana, Prometheus und OpenTelemetry zur Verfolgung des Transaktionsdurchsatzes und Kafka-Consumer-Lag.
- Leitete Systemdesign-Reviews und Code-Architektur für kritische datenbankgestützte Dienste, mentorierte Junior-Ingenieure zu skalierbaren Mustern der Datenpersistenz.

### Seed Labs - Software Engineer
Pakistan | 06/2020 - 06/2021
- Entwickelte Data-ETL-Pipelines und analytische Workflows mit Python und SQL, bereinigte und transformierte Rohdatensätze für Stakeholder-Berichte.
- Entwickelte Diagramme zur Datenvisualisierung und Insights-Dashboards zur Kommunikation analytischer Erkenntnisse, nutzte MySQL und MongoDB für persistente Datenspeicherung.

## Ausbildung

### Technical University of Ilmenau
Master of Research, Computer Systems and Engineering | 04/2024 - Present

### National University of Computer and Engineering Sciences
Bachelor of Science, Computer Science | 06/2016 - 08/2020

## Projekte

### My Notebook (Document RAG) ([portfolio](https://radheem.github.io/my-cv/projects/my-notebook/))
- Erstellte eine robuste, wiederholbare Dokumenten-Ingestion-Pipeline mit Hatchet (extract → chunk → embed → summarize → index) mit Timeout-Einstellungen pro Schritt und absturzsicheren Wiederholungen.
- Implementierte Vektorsuche mit pgvector (HNSW, cosine) und Echtzeit-Fortschritts-Streaming über NATS JetStream + SSE für persistente Zustandsverfolgung.
- Bereitgestellt als Cloud-Native-App auf k3d mit cert-manager TLS und ExternalDNS, wobei alle Inferences lokal über zwei llama.cpp-Server hinter einer OpenAI-kompatiblen API gehalten wurden.

### cv-tailor (LLM CV/Cover Tailoring + LinkedIn Automation) ([portfolio](https://radheem.github.io/my-cv/projects/cv-tailor/))
- Entwickelte eine Python-CLI und einen **FastMCP Server** zur Automatisierung der CV/Anschreiben-Anpassung mit unit-getesteter Projekt-Ranking (Anthropic/Ollama) und Halluzinations-Schutz.
- Entwickelte eine automatisierte **Gmail alert ingestion**-Pipeline und leichtgewichtiges Guest-API-Fetching, integriert mit bidirektionaler **Google Sheets synchronization** für Lifecycle-Tracking.
- Sicherte sensible Dokumente in Git mit clientseitiger **AES-256-GCM**-Verschlüsselung, geschützt durch passwortgeschützte statische Pages.

## Kenntnisse

- Sprachen (gesprochen): Englisch (fließend), Deutsch (A2)
- Datenbanken & Persistenz: PostgreSQL (sqlc), MySQL, MongoDB/DocumentDB, Dgraph, DynamoDB, BigQuery, Snowflake
- Daten & Analytics: pandas, scikit-learn, Kubeflow Pipelines, KServe, Grafana, VictoriaMetrics
- Programmiersprachen: Python, SQL, Go, TypeScript, JavaScript, Bash, PHP
- Systeme & ETL/Streaming: Kafka, NATS (JetStream + KV), Hatchet, MCP (FastMCP), gRPC, Dapr, OpenTelemetry
- Cloud/Infra & Architektur: Kubernetes, kustomize, Skaffold, Cilium, external-dns, Docker, Helm, Terraform, AWS (EC2, RDS, DynamoDB)
- Web: ReactJS, NodeJS, NestJS, Django
