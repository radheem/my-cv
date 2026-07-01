---
tagline: "Praktikum: Technologie, Daten & Innovation 2026"
---

## Berufserfahrung

### Al Hilal Invest - Senior Software Engineer
Pakistan | 11/2023 - 03/2024
- Containerisierte Backend-Dienste mit Docker und orchestrierte Bereitstellungen auf AWS EC2 und Kubernetes, wodurch Release-Pipelines und Plattform-Skalierbarkeit optimiert wurden.
- Leitete Architektur-Reviews der Plattform und definierte Code-Qualitätsstandards mit Fokus auf skalierbare Infrastruktur, DevOps-Praktiken und Systemzuverlässigkeit.
- Entwickelte und dokumentierte cloud-native Service-Integrationen, um hohe Verfügbarkeit und robuste Bereitstellungsprozesse zu gewährleisten.
Tech: NodeJS, PHP, TypeScript, ReactJS, Docker, MySQL, MongoDB, AWS S3, AWS EC2, Kubernetes.

### Bluefin Exchange - Senior Software Engineer
Pakistan | 06/2021 - 08/2023
- Entwickelte umfassende Observability-Stacks mit Prometheus, OpenTelemetry und Grafana zur Überwachung der Transaktions-Engine-Durchsatzleistung und des Kafka-Consumer-Lags, wodurch Latenzspitzen proaktiv reduziert und die Plattformzuverlässigkeit verbessert wurden.
- Orchestrierte CI/CD-Release-Prozesse und Infrastructure-as-Code (Terraform) für Kubernetes-basierte Microservices, wobei GitOps-Prinzipien und Plattformstabilität durchgesetzt wurden.
- Konzipierte und implementierte skalierbare Plattformarchitekturen und optimierte verteilte Systeme für hohe Verfügbarkeit und Latenzarmut.
- Trat als fachlicher Experte für Plattform-Systemdesign-Reviews auf und sicherte die Einhaltung von SRE-Best-Practices und Observability-Standards.
- Betreute Engineering-Teams in den Bereichen cloud-native Entwicklung, Kubernetes-Betrieb und observability-gesteuertes Debugging.
Tech: ReactJS, NodeJS, Go, Python, TypeScript, Docker, PostgreSQL, DynamoDB, Kafka, Terraform, Kubernetes, Prometheus, Grafana, OpenTelemetry.

### Seed Labs - Software Engineer
Pakistan | 06/2020 - 06/2021
- Arbeitete in funktionsübergreifenden Engineering-Teams zusammen, um containerisierte Anwendungen mit Docker und AWS EC2-Infrastruktur auszuliefern, mit Fokus auf automatisierte Deployment-Workflows.
- Erkundete und prototypisierte skalierbare Backend-Architekturen und Automatisierungsskripte, um Data-Pipeline-Deployments und Plattformintegrationen zu beschleunigen.
- Entwickelte automatisierte Data-Processing-Pipelines und Visualisierungs-Dashboards, integrierte Infrastrukturmetriken für operationale Transparenz und Zuverlässigkeitsverfolgung.
Tech: Python, scikit-learn, NodeJS, TensorFlow, Docker, MongoDB, MySQL, AWS EC2.

## Ausbildung

### Technical University of Ilmenau
Master of Research, Computer Systems and Engineering | 04/2024 - Present

### National University of Computer and Engineering Sciences
Bachelor of Science, Computer Science | 06/2016 - 08/2020

## Projekte

### cv-tailor - LLM CV/Cover-Letter Tailoring + LinkedIn Automation
- Entwickelte eine Python-CLI und einen FastMCP-Server, der die Anpassung von Lebenslauf und Anschreiben automatisiert, indem unit-getestete Projekt-Rankings (Anthropic/Ollama) verwendet werden und vor Halluzinationen geschützt wird.
- Entwickelte eine automatisierte Gmail-Alert-Ingestion-Pipeline (LinkedIn, Glassdoor, Indeed, Fraunhofer) sowie leichtgewichtiges Guest-API-Fetching, um zuverlässige Datensynchronisation und Plattformzustandsverwaltung zu gewährleisten.
- Integrierte eine bidirektionale Google-Sheets-Synchronisation über Google Apps Script zur Nachverfolgung von Bewerbungslebenszyklen und Automatisierung von Workflow-Übergängen.
- Sicherte Dokumente in Git mittels clientseitiger AES-256-GCM-Verschlüsselung, die über passwortgeschützte statische Pages freigeschaltet wird, und durchsetzte Zero-Trust-Datenverarbeitung sowie Platformsicherheit.

### Second Brain - Self-Hosted Document RAG
- Entwickelte eine robuste, wiederholbare Document-Ingestion-Pipeline mit Hatchet (extract → chunk → embed → summarize → index) mit schrittweisen Timeouts und Retries, instrumentiert mit OpenTelemetry und benutzerdefinierten Grafana-Dashboards.
- Konzipierte Echtzeit-Fortschritts-Streaming über NATS JetStream + SSE (durable stream + KV current-state), um zuverlässige ereignisgesteuerte Kommunikation und Plattform-Observability zu gewährleisten.
- Hielt alle Inference-Prozesse lokal und privat über zwei llama.cpp-Server (chat + embeddings) hinter einer OpenAI-kompatiblen API, wodurch die Plattform-Ressourcennutzung und Netzwerkisolation optimiert wurden.
- Implementierte Vektorsuche mit pgvector (HNSW, cosine); bereitete cloud-native auf k3d mit cert-manager TLS und ExternalDNS vor, um sichere DNS-Auflösung und Plattformverfügbarkeit zu gewährleisten.

### Information Retrieval System (IRS) - Distributed Systems Platform
- Bereitgestellt mit Kubernetes, kustomize, Skaffold, Cilium und external-dns; integrierte OpenTelemetry Distributed Tracing und Prometheus-Metriksammlung über alle Go-Microservices hinweg.
- Migrierte die Plattform von Dapr zu nativem NATS JetStream (Messaging), NATS KV (Session State) und direktem gRPC, wodurch der Plattform-Overhead reduziert und die Netzwerkzuverlässigkeit verbessert wurde.
- Entwickelte einen Best-Effort-ETL-Side-Channel in PostgreSQL (sqlc), Dgraph und DocumentDB, orchestriert von Hatchet mit deklarativem Routing; verifiziert durch ein Ginkgo E2E Gate.
- Entwickelte Go-Microservices mit gRPC und gRPC-Gateway unter Verwendung von Protobuf-first APIs und Buf-Tooling, wodurch eine robuste, observable Plattformbasis mit Consistent-Hashing-Gateways etabliert wurde.

## Kenntnisse

- Sprachen (gesprochen): Englisch (fließend), Deutsch (A2)
- Cloud & Platform-Infra: Kubernetes, Cilium, Docker, Helm, kustomize, Skaffold, external-dns, Terraform, AWS (EC2, RDS, DynamoDB)
- Observability & SRE: OpenTelemetry, Prometheus, Grafana, VictoriaMetrics, Distributed Tracing, Metriksammlung, Alerting, Reliability Engineering
- Networking & Messaging: NATS (JetStream + KV), Kafka, gRPC, Dapr
- Programmiersprachen: Go, Python, SQL, TypeScript, JavaScript, Bash, PHP
- Datenbanken: PostgreSQL (sqlc), MySQL, MongoDB/DocumentDB, Dgraph, DynamoDB, BigQuery, Snowflake
- Web: ReactJS, NodeJS, NestJS, Django
- ML/Data: Kubeflow Pipelines, KServe, scikit-learn, TensorFlow/Keras, pandas
