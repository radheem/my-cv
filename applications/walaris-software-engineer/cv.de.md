---
tagline: "Software Engineer"
---

## Berufserfahrung

### AiVader GmbH - Research Engineering Intern
Germany | 02/2026 - 04/2026
- Integration und Bereitstellung eines reproduzierbaren 5G Standalone (SA) Testbed O RAN AI/ML Framework mit runbook-konfigurierten Bereitstellungen.
- Entwicklung einer xApp zur Extraktion von Live-Funkleistungs-Telemetriedaten über die E2-Schnittstelle und Veröffentlichung in einem Message Broker, wodurch eine hochauflösende Datenquelle für die KI/ML-Extraktion bereitgestellt wurde.
- Training und Bereitstellung von QoE-Durchsatzvorhersagemodellen mit Kubeflow Pipelines und KServe zur Ermöglichung von Echtzeit-Inferenz.
- Tech: Kubeflow, KServe, Cassandra, Python, InfluxDB, Kafka, Kubernetes, Docker, Linux.

### Al Hilal Invest - Senior Software Engineer
Pakistan | 11/2023 - 03/2024
- Architektur und Containerisierung von Backend-Diensten auf Kubernetes und AWS zur Optimierung von Deployment-Pipelines für skalierbare Plattform-Infrastruktur.
- Leitung von Systemdesign und Code Reviews, Festlegung robuster Architekturmuster für verteilte Microservices und Cloud-Native-Deployments.
- Entwicklung und Dokumentation hochperformanter Dienste mit NodeJS, TypeScript und Docker zur Sicherstellung eines zuverlässigen Backend-Betriebs.

### Bluefin Exchange - Senior Software Engineer
Pakistan | 06/2021 - 08/2023
- Integration von OpenTelemetry, Prometheus und Grafana in verteilte Go/Python-Dienste zur Überwachung des Systemdurchsatzes und Reduzierung von Latenzspitzen.
- Identifikation und Umsetzung von Systemdesign-Verbesserungen für Kern-Börsendienste zur Optimierung der Infrastrukturreliabilität und Observability.
- Pflege von Release-Prozessen und Leitung von Junior-Engineering-Teams zur Sicherstellung konsistenter Deployment-Standards und Plattformstabilität.

## Ausbildung

### Technische Universität Ilmenau
Master of Research, Computer Systems and Engineering | 04/2024 - Present

### National University of Computer and Engineering Sciences
Bachelor of Science, Computer Science | 06/2016 - 08/2020

## Projekte

### My Notebook (Document RAG) ([portfolio](https://radheem.github.io/my-cv/projects/my-notebook/))
- Ausfallsichere, wiederholbare Dokumenten-Ingestion-Pipeline mit Hatchet (extract → chunk → embed → summarize → index) mit Timeout- und Retry-Steuerung pro Schritt sowie OpenTelemetry-Instrumentierung.
- Echtzeit-Fortschritts-Streaming über NATS JetStream + SSE, wobei alle lokalen Inferenzen über zwei llama.cpp-Server hinter einer OpenAI-kompatiblen API gesichert sind.
- Vektorsuche implementiert mit pgvector (HNSW, cosine); Cloud-Native-Deployment auf k3d mit cert-manager TLS und ExternalDNS.

### Data Analyzer ([portfolio](https://radheem.github.io/my-cv/projects/data-analyzer/))
- Aufbau eines Python Model Context Protocol (MCP) Servers mit `FastMCP` zur Bereitstellung optimierter BigQuery-Tools für LLM-Agents, wodurch Roh-SQL-Token-Spitzen eliminiert und der Dataset-Zugriff gesichert wurde.
- Orchestrierung der Docker Compose-Synchronisation zwischen dem benutzerdefinierten Python FastMCP Server, Grafana und dem offiziellen Grafana MCP Server zur Ermöglichung einer deklarativen, agentic-Steuerung von Dashboards.
- Automatisierte Zero-Touch-Bereitstellung von GCP-Anmeldeinformationen, Grafana Service Accounts und BigQuery-Datasources beim Booten zur Sicherstellung sofortiger Betriebsbereitschaft.

## Kenntnisse

- Sprachen (gesprochen): Englisch (fließend), Deutsch (A2)
- KI/ML & MLOps: Kubeflow Pipelines, KServe, scikit-learn, TensorFlow/Keras, pandas, pgvector, vector-search, inference, model-training, agentic agents, LLM orchestration, RAG pipelines
- Cloud & Infrastruktur: Kubernetes, Helm, kustomize, Skaffold, Docker, Terraform, AWS (EC2, RDS, DynamoDB), Cilium, external-dns
- Systeme & Messaging: gRPC, NATS (JetStream + KV), Hatchet, MCP (FastMCP), Kafka, Dapr, OpenTelemetry, VictoriaMetrics, Grafana
- Datenbanken: PostgreSQL (sqlc), MySQL, MongoDB/DocumentDB, Dgraph, DynamoDB, BigQuery, Snowflake
- Programmiersprachen: Python, Go, SQL, TypeScript, JavaScript, Bash, PHP
- Web & Frameworks: ReactJS, NodeJS, NestJS, Django
