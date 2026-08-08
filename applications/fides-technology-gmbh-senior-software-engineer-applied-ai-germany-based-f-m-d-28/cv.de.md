---
tagline: "Senior Software Engineer for Applied AI"
---

## Berufserfahrung

### AiVader GmbH - Research Engineering Intern
Germany | 02/2026 - 04/2026
- Integrierte und bereitete ein reproduzierbares 5G-Standalone-(SA)-Testbed sowie ein O-RAN-AI/ML-Framework mit runbook-konfigurierten Deployments vor.
- Entwickelte eine xApp zur Extraktion von Echtzeit-Telemetriedaten zur Funkleistungsüberwachung über die E2-Schnittstelle und deren Veröffentlichung in einem Message Broker, um eine hochauflösende Datenquelle für die KI/ML-Analyse bereitzustellen.
- Trainierte und bereitete QoE-Durchsatzvorhersagemodelle mit Kubeflow Pipelines und KServe ein, um Echtzeit-Inferenz zu ermöglichen.
- Tech: Kubeflow, KServe, Cassandra, Python, InfluxDB, Kafka, Kubernetes, Docker, Linux.

### Al Hilal Invest - Senior Software Engineer
Pakistan | 11/2023 - 03/2024
- Architekturierte und containerisierte Backend-Dienste auf Kubernetes und AWS, optimierte Deployments-Pipelines für eine skalierbare Plattforminfrastruktur.
- Leitete Systemdesign und Code-Reviews, etablierte robuste Architekturmuster für verteilte Microservices und cloud-native Deployments.
- Entwickelte und dokumentierte hochperformante Dienste mit NodeJS, TypeScript und Docker, um zuverlässige Backend-Betriebprozesse sicherzustellen.

### Bluefin Exchange - Senior Software Engineer
Pakistan | 06/2021 - 08/2023
- Integrierte OpenTelemetry, Prometheus und Grafana in verteilte Go/Python-Dienste zur Überwachung des Systemdurchsatzes und zur Reduzierung von Latenzspitzen.
- Identifizierte und implementierte Systemdesign-Verbesserungen für Kern-Börsendienste, optimierte die Zuverlässigkeit und Observability der Infrastruktur.
- Pflegte Release-Prozesse und leitete Junior-Engineering-Teams, um konsistente Deployment-Standards und Plattformstabilität sicherzustellen.

## Ausbildung

### Technical University of Ilmenau
Master of Research, Computer Systems and Engineering | 04/2024 - Heute

### National University of Computer and Engineering Sciences
Bachelor of Science, Computer Science | 06/2016 - 08/2020

## Projekte

### My Notebook (Document RAG) ([portfolio](https://radheem.github.io/my-cv/projects/my-notebook/))
- Robuste, wiederholbare Dokumenten-Ingestion-Pipeline mit Hatchet (extrahieren → chunken → embedden → zusammenfassen → indexieren) mit schrittweisen Timeouts, Wiederholungsmechanismen und OpenTelemetry-Instrumentierung.
- Echtzeit-Fortschritts-Streaming über NATS JetStream + SSE, wobei alle lokalen Inferenzen über zwei llama.cpp-Server hinter einer OpenAI-kompatiblen API gesichert sind.
- Vektorsuche implementiert mit pgvector (HNSW, cosine); cloud-nativ auf k3d mit cert-manager TLS und ExternalDNS bereitgestellt.

### Data Analyzer ([portfolio](https://radheem.github.io/my-cv/projects/data-analyzer/))
- Entwickelte einen Python Model Context Protocol (MCP)-Server mit `FastMCP`, um optimierte BigQuery-Tools für LLM-Agents bereitzustellen, rohe SQL-Token-Spitzen zu eliminieren und den Dataset-Zugriff zu sichern.
- Orchestrierte Docker-Compose-Synchronisation zwischen dem benutzerdefinierten Python FastMCP-Server, Grafana und dem offiziellen Grafana MCP-Server, um eine deklarative, agentenbasierte Steuerung von Dashboards zu ermöglichen.
- Automatisierte die Zero-Touch-Bereitstellung von GCP-Anmeldeinformationen, Grafana-Service-Accounts und BigQuery-Datenquellen beim Systemstart, um sofortige Betriebsbereitschaft zu gewährleisten.

## Kenntnisse

- Sprachen (gesprochen): Englisch (fließend), Deutsch (A2)
- KI/ML & MLOps: Kubeflow Pipelines, KServe, scikit-learn, TensorFlow/Keras, pandas, pgvector, Vektorsuche, Inferenz, Modelltraining, agentenbasierte Agenten, LLM-Orchestrierung, RAG-Pipelines
- Cloud & Infrastruktur: Kubernetes, Helm, kustomize, Skaffold, Docker, Terraform, AWS (EC2, RDS, DynamoDB), Cilium, external-dns
- Systeme & Messaging: gRPC, NATS (JetStream + KV), Hatchet, MCP (FastMCP), Kafka, Dapr, OpenTelemetry, VictoriaMetrics, Grafana
- Datenbanken: PostgreSQL (sqlc), MySQL, MongoDB/DocumentDB, Dgraph, DynamoDB, BigQuery, Snowflake
- Programmiersprachen: Python, Go, SQL, TypeScript, JavaScript, Bash, PHP
- Web & Frameworks: ReactJS, NodeJS, NestJS, Django
