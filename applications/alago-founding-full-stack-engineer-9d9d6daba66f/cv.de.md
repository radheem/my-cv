---
tagline: "Full-Stack Engineer"
---

## Berufserfahrung

### Al Hilal Invest - Senior Software Engineer
Pakistan | 11/2023 - 03/2024
- Backend-Dienste entworfen und in Docker-Container verpackt, Systemdesign-Reviews geleitet, um die Datenspeicherung und Transaktionsabläufe über MySQL und MongoDB hinweg zu optimieren.
- Datengetriebene Funktionen und APIs entwickelt, robuste Dokumentationsstandards für skalierbare Informationsverwaltungssysteme etabliert.
- Bereitstellungs-Pipelines und Infrastruktur-Bereitstellung auf AWS EC2 und Kubernetes optimiert, um hochverfügbare Daten-Dienste zu unterstützen.

### Bluefin Exchange - Senior Software Engineer
Pakistan | 06/2021 - 08/2023
- Leistung der Transaktions-Engine und Datenspeicherung durch Integration von PostgreSQL und DynamoDB optimiert, wodurch Latenzspitzen in hochdurchsatzstarken Börsendiensten direkt reduziert wurden.
- Umfassende Dashboards für Datenanalyse und Monitoring mit Grafana, Prometheus und OpenTelemetry entworfen und implementiert, um Transaktionsdurchsatz und Kafka consumer lag zu verfolgen.
- Systemdesign-Reviews und Code-Architektur für kritische, datenbankgestützte Dienste geleitet, Junior-Ingenieure bei skalierbaren Mustern der Datenspeicherung betreut.

### Seed Labs - Software Engineer
Pakistan | 06/2020 - 06/2021
- Daten-ETL-Pipelines und analytische Workflows mit Python und SQL entwickelt, Rohdatensätze für das Reporting an Stakeholder bereinigt und transformiert.
- Datenvisualisierungen und Insights-Dashboards zur Darstellung analytischer Ergebnisse entwickelt, wobei MySQL und MongoDB für die persistente Datenspeicherung genutzt wurden.

## Ausbildung

### Technical University of Ilmenau
Master of Research, Computer Systems and Engineering | 04/2024 - Present

### National University of Computer and Engineering Sciences
Bachelor of Science, Computer Science | 06/2016 - 08/2020

## Projekte

### My Notebook (Document RAG) ([portfolio](https://radheem.github.io/my-cv/projects/my-notebook/))
- Robuste, wiederholbare Dokumenten-Ingestion-Pipeline mit Hatchet (extract → chunk → embed → summarize → index) aufgebaut, mit Timeout-Einstellungen pro Schritt und absturzsicheren Wiederholungen.
- Vektorsuche mit pgvector (HNSW, cosine) und Echtzeit-Fortschritts-Streaming über NATS JetStream + SSE für persistente Statusverfolgung implementiert.
- Cloud-nativ auf k3d mit cert-manager TLS und ExternalDNS bereitgestellt, wobei alle Inferenzen lokal über zwei llama.cpp-Server hinter einer OpenAI-kompatiblen API gehalten wurden.

### cv-tailor (LLM CV/Cover Tailoring + LinkedIn Automation) ([portfolio](https://radheem.github.io/my-cv/projects/cv-tailor/))
- Python-CLI und **FastMCP Server** entwickelt, die die Anpassung von Lebenslauf und Anschreiben automatisieren, mit unit-getesteter Projekt-Ranking (Anthropic/Ollama) und Halluzinations-Schutzmechanismen.
- Automatisierte **Gmail alert ingestion**-Pipeline und leichtgewichtiges Guest-API-Fetching entwickelt, integriert mit bidirektionaler **Google Sheets synchronization** zur Lebenszyklus-Verfolgung.
- Sensible Dokumente in Git mittels clientseitiger **AES-256-GCM**-Verschlüsselung gesichert, geschützt durch passwortgeschützte statische Pages.

## Kenntnisse

- Sprachen (gesprochen): Englisch (fließend), Deutsch (A2)
- Datenbanken & Persistenz: PostgreSQL (sqlc), MySQL, MongoDB/DocumentDB, Dgraph, DynamoDB, BigQuery, Snowflake
- Daten & Analytik: pandas, scikit-learn, Kubeflow Pipelines, KServe, Grafana, VictoriaMetrics
- Programmiersprachen: Python, SQL, Go, TypeScript, JavaScript, Bash, PHP
- Systeme & ETL/Streaming: Kafka, NATS (JetStream + KV), Hatchet, MCP (FastMCP), gRPC, Dapr, OpenTelemetry
- Cloud/Infra & Architektur: Kubernetes, kustomize, Skaffold, Cilium, external-dns, Docker, Helm, Terraform, AWS (EC2, RDS, DynamoDB)
- Web: ReactJS, NodeJS, NestJS, Django
