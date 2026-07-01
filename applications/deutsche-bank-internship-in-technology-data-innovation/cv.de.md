---
tagline: "Praktikum im Bereich Technologie, Daten & Innovation"
---

## Berufserfahrung

### Al Hilal Invest - Senior Software Engineer
Pakistan | 11/2023 - 03/2024
- Containerisierung von Backend-Diensten mit Docker sowie orchestrierte Bereitstellungen auf AWS EC2 und Kubernetes zur Optimierung von Release-Pipelines und Plattform-Skalierbarkeit.
- Leitung von Plattform-Architektur-Reviews und Definition von Code-Qualitätsstandards mit Fokus auf skalierbare Infrastruktur, DevOps-Praktiken und Systemzuverlässigkeit.
- Entwicklung und Dokumentation cloud-native Service-Integrationen, um hohe Verfügbarkeit und robuste Bereitstellungsprozesse zu gewährleisten.
Tech: NodeJS, PHP, TypeScript, ReactJS, Docker, MySQL, MongoDB, AWS S3, AWS EC2, Kubernetes.

### Bluefin Exchange - Senior Software Engineer
Pakistan | 06/2021 - 08/2023
- Entwicklung umfassender Observability-Stacks mit Prometheus, OpenTelemetry und Grafana zur Überwachung der Transaktions-Engine-Durchsatzleistung und des Kafka-Consumer-Lags, wodurch Latenzspitzen proaktiv reduziert und die Plattformzuverlässigkeit verbessert wurden.
- Orchestrierung von CI/CD-Release-Prozessen und Infrastructure-as-Code (Terraform) für Kubernetes-basierte Microservices, wodurch GitOps-Prinzipien durchgesetzt und die Plattformstabilität sichergestellt wurden.
- Entwurf und Implementierung skalierbarer Plattformarchitekturen und Optimierung verteilter Systeme für hohe Verfügbarkeit und latenzarme Performance.
- Auftritt als Plattform-Experte für Systemdesign-Reviews und Sicherung der Einhaltung von SRE-Best-Practices und Observability-Standards.
- Mentoring von Engineering-Teams in den Bereichen cloud-native Entwicklung, Kubernetes-Operationen und observability-gesteuertes Debugging.
Tech: ReactJS, NodeJS, Go, Python, TypeScript, Docker, PostgreSQL, DynamoDB, Kafka, Terraform, Kubernetes, Prometheus, Grafana, OpenTelemetry.

### Seed Labs - Software Engineer
Pakistan | 06/2020 - 06/2021
- Zusammenarbeit in funktionsübergreifenden Engineering-Teams zur Bereitstellung containerisierter Anwendungen mit Docker und AWS EC2-Infrastruktur, mit Fokus auf automatisierte Deployment-Workflows.
- Recherche und Prototypisierung skalierbarer Backend-Architekturen und Automatisierungsskripte zur Optimierung von Data-Pipeline-Deployments und Plattformintegration.
- Entwicklung automatisierter Data-Processing-Pipelines und Visualisierungs-Dashboards, die Infrastrukturmetriken für operationale Transparenz und Zuverlässigkeitsverfolgung integrieren.
Tech: Python, scikit-learn, NodeJS, TensorFlow, Docker, MongoDB, MySQL, AWS EC2.

## Ausbildung

### Technical University of Ilmenau
Master of Research, Computer Systems and Engineering | 04/2024 - Present

### National University of Computer and Engineering Sciences
Bachelor of Science, Computer Science | 06/2016 - 08/2020

## Projekte

### cv-tailor - LLM CV/Cover-Letter Tailoring + LinkedIn Automation
- Entwicklung einer Python-CLI und eines FastMCP-Servers, der die Anpassung von Lebenslauf und Anschreiben automatisiert, indem unit-getestetes Projekt-Ranking (Anthropic/Ollama) genutzt und Halluzinationen vorgebeugt wird.
- Entwicklung einer automatisierten Gmail-Alert-Ingestion-Pipeline (LinkedIn, Glassdoor, Indeed, Fraunhofer) sowie leichtgewichtigem Guest-API-Fetching, um zuverlässige Datensynchronisation und Plattform-Statusverwaltung zu gewährleisten.
- Integration einer bidirektionalen Google-Sheets-Synchronisierung mittels Google Apps Script zur Verfolgung von Bewerbungslebenszyklen und Automatisierung von Workflow-Übergängen.
- Sicherung von Dokumenten in Git mittels clientseitiger AES-256-GCM-Verschlüsselung, die über passwortgeschützte statische Pages freigeschaltet wird, um Zero-Trust-Datenverarbeitung und Platformsicherheit durchzusetzen.

### Second Brain - Self-Hosted Document RAG
- Entwicklung einer robusten, wiederholbaren Document-Ingestion-Pipeline mit Hatchet (extract → chunk → embed → summarize → index) mit schrittweisen Timeouts und Retries, instrumentiert mit OpenTelemetry und individuellen Grafana-Dashboards.
- Entwurf von Echtzeit-Progress-Streaming über NATS JetStream + SSE (durable stream + KV current-state), um zuverlässige event-gesteuerte Kommunikation und Plattform-Observability zu gewährleisten.
- Lokale und private Ausführung aller Inference-Prozesse über zwei llama.cpp-Server (chat + embeddings) hinter einer OpenAI-kompatiblen API, zur Optimierung der Plattform-Ressourcennutzung und Netzwerkisolation.
- Implementierung der Vektorsuche mit pgvector (HNSW, cosine); cloud-native Bereitstellung auf k3d mit cert-manager TLS und ExternalDNS, um sichere DNS-Auflösung und Plattform-Verfügbarkeit zu gewährleisten.

### Information Retrieval System (IRS) - Distributed Systems Platform
- Bereitstellung mit Kubernetes, kustomize, Skaffold, Cilium und external-dns; Integration von OpenTelemetry Distributed Tracing und Prometheus-Metrik-Sammlung über alle Go-Microservices hinweg.
- Migration der Plattform von Dapr zu nativem NATS JetStream (Messaging), NATS KV (Session State) und direktem gRPC, wodurch Plattform-Overhead reduziert und Netzwerkzuverlässigkeit verbessert wurde.
- Entwicklung eines Best-Effort ETL Side-Channel in PostgreSQL (sqlc), Dgraph und DocumentDB, orchestriert von Hatchet mit deklarativer Routing; verifiziert durch ein Ginkgo E2E Gate.
- Entwicklung von Go-Microservices mit gRPC und gRPC-Gateway auf Basis von Protobuf-first APIs und Buf-Tooling, wodurch eine robuste, observable Plattformbasis mit Consistent-Hashing-Gateways etabliert wurde.

## Kenntnisse

- Sprachen (gesprochen): Englisch (fließend), Deutsch (A2)
- Cloud & Platform Infra: Kubernetes, Cilium, Docker, Helm, kustomize, Skaffold, external-dns, Terraform, AWS (EC2, RDS, DynamoDB)
- Observability & SRE: OpenTelemetry, Prometheus, Grafana, VictoriaMetrics, distributed tracing, metrics collection, alerting, reliability engineering
- Networking & Messaging: NATS (JetStream + KV), Kafka, gRPC, Dapr
- Programmiersprachen: Go, Python, SQL, TypeScript, JavaScript, Bash, PHP
- Databases: PostgreSQL (sqlc), MySQL, MongoDB/DocumentDB, Dgraph, DynamoDB, BigQuery, Snowflake
- Web: ReactJS, NodeJS, NestJS, Django
- ML/Data: Kubeflow Pipelines, KServe, scikit-learn, TensorFlow/Keras, pandas
