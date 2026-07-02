---
tagline: "QA Engineer / Software Tester"
---

## Berufserfahrung

### Al Hilal Invest - Senior Software Engineer
Pakistan | 11/2023 - 03/2024
- Backend-Dienste entworfen und in Docker containerisiert, Systemdesign-Reviews geleitet zur Optimierung der Datenpersistenz und transaktionaler Workflows über MySQL und MongoDB.
- Neue datengetriebene Features und APIs entwickelt, robuste Dokumentationsstandards für skalierbare Informationsmanagementsysteme etabliert.
- Deployment-Pipelines und Infrastruktur-Bereitstellung auf AWS EC2 und Kubernetes optimiert, um hochverfügbare Daten-Dienste zu unterstützen.

### Bluefin Exchange - Senior Software Engineer
Pakistan | 06/2021 - 08/2023
- Leistung der Transaktions-Engine und Datenpersistenz durch Integration von PostgreSQL und DynamoDB optimiert, wodurch Latenzspitzen in durchsatzstarken Börsen-Diensten direkt reduziert wurden.
- Umfassende Dashboards für Datenanalyse und Monitoring mit Grafana, Prometheus und OpenTelemetry entworfen und implementiert, um Transaktionsdurchsatz und Kafka Consumer Lag zu verfolgen.
- Systemdesign-Reviews und Code-Architektur für kritische datenbankgestützte Dienste geleitet; Junior-Engineers in skalierbaren Mustern der Datenpersistenz betreut.

### Seed Labs - Software Engineer
Pakistan | 06/2020 - 06/2021
- Daten-ETL-Pipelines und analytische Workflows mit Python und SQL entwickelt, Rohdaten bereinigt und transformiert für Reporting an Stakeholder.
- Datenvisualisierungen und Insights-Dashboards zur Darstellung analytischer Erkenntnisse entwickelt, unter Nutzung von MySQL und MongoDB für persistente Datenspeicherung.

## Ausbildung

### Technical University of Ilmenau
Master of Research, Computer Systems and Engineering | 04/2024 - Present

### National University of Computer and Engineering Sciences
Bachelor of Science, Computer Science | 06/2016 - 08/2020

## Projekte

### Second Brain (Document RAG) ([repo](https://github.com/radheem/my-notebook))
- Robuste, wiederholbare Dokumenten-Ingestion-Pipeline mit Hatchet (extract → chunk → embed → summarize → index) aufgebaut, mit Timeout pro Schritt und absturzsicheren Wiederholungsversuchen.
- Vektorsuche mit pgvector (HNSW, cosine) sowie Echtzeit-Progress-Streaming über NATS JetStream + SSE für persistente Statusverfolgung implementiert.
- Cloud-native auf k3d mit cert-manager TLS und ExternalDNS bereitgestellt, wobei alle Inferences lokal über zwei llama.cpp-Server hinter einer OpenAI-kompatiblen API gehalten wurden.

### cv-tailor (LLM CV/Cover Tailoring + LinkedIn Automation) ([repo](https://github.com/radheem/cv-tailor))
- Python-CLI und **FastMCP Server** entwickelt, die die Anpassung von Lebenslauf und Anschreiben automatisieren, mit unit-getesteter Projekt-Ranking (Anthropic/Ollama) und Halluzinations-Schutzmechanismen.
- Automatisierte **Gmail-Alert-Ingestion**-Pipeline und leichtgewichtiges Guest-API-Fetching entwickelt, integriert mit bidirektionaler **Google Sheets-Synchronisation** zur Lebenszyklus-Verfolgung.
- Sensible Dokumente in Git durch clientseitige **AES-256-GCM**-Verschlüsselung gesichert, geschützt hinter passwortgeschützten statischen Pages.

## Kenntnisse

- Sprachen (gesprochen): Englisch (fließend), Deutsch (A2)
- Datenbanken & Persistenz: PostgreSQL (sqlc), MySQL, MongoDB/DocumentDB, Dgraph, DynamoDB, BigQuery, Snowflake
- Daten & Analytik: pandas, scikit-learn, Kubeflow Pipelines, KServe, Grafana, VictoriaMetrics
- Programmiersprachen: Python, SQL, Go, TypeScript, JavaScript, Bash, PHP
- Systeme & ETL/Streaming: Kafka, NATS (JetStream + KV), Hatchet, MCP (FastMCP), gRPC, Dapr, OpenTelemetry
- Cloud/Infra & Architektur: Kubernetes, kustomize, Skaffold, Cilium, external-dns, Docker, Helm, Terraform, AWS (EC2, RDS, DynamoDB)
- Web: ReactJS, NodeJS, NestJS, Django
