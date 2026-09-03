---
tagline: "Backend-Entwickler"
---

## Berufserfahrung

### AiVader GmbH - Research Engineering Intern
Germany | 02/2026 - 04/2026
- Aufbau einer reproduzierbaren ZeroMQ-basierten virtuellen RF-Lockstep-Pipeline für die deterministische 5G-Standalone-RAN-Emulation; Stabilisierung der Lockstep-Wiederverbindungsmechaniken und Container-Lebenszyklen.
- Entwicklung einer maßgeschneiderten xApp, die gNB-Metriken über die E2-Schnittstelle abfragt und Echtzeit-Telemetriedaten an einen Kafka-Pub-Sub-Broker sendet, wodurch Nachrichten-Durchsatz und Latenz optimiert wurden.
- Bereitstellung des Multi-Container-Open-Source-Stacks für den produktiven Einsatz, einschließlich Debugging und Behebung mehrerer Betriebsprobleme.
- Tech: ZeroMQ, Kafka, Python, Go, MongoDB, InfluxDB, Docker, Linux, C++.

### Al Hilal Invest - Senior Software Engineer
Pakistan | 11/2023 - 03/2024
- Architektur und Containerisierung von Backend-Services mit NodeJS, TypeScript und Docker; Optimierung der Deployment-Pipelines auf AWS EC2 und Kubernetes.
- Leitung von Systemdesign- und Code-Reviews; Festlegung architektonischer Standards für skalierbare Microservices und API-Entwicklung.
- Entwicklung und Dokumentation neuer Fullstack-Features unter Integration von ReactJS, MySQL und MongoDB; Verbesserung der Service-Zuverlässigkeit und Entwicklerproduktivität.

### Bluefin Exchange - Senior Software Engineer
Pakistan | 06/2021 - 08/2023
- Entwicklung hochperformanter Transaktions-Services in Go und NodeJS; Implementierung von Verbesserungen im verteilten Systemdesign zur Eliminierung von Latenzspitzen.
- Integration von OpenTelemetry-Metriken, Prometheus-Logging und Grafana-Alerts zur Überwachung des Kafka-Consumer-Group-Lags und Backend-Durchsatzes über Microservices hinweg.
- Mentoring von Junior-Entwicklern und Pflege der Release-Prozesse für Kern-Börsenservices; Sicherstellung einer robusten API-Architektur und Systemobservierbarkeit.

## Ausbildung

### Technical University of Ilmenau
Master of Research, Computer Systems and Engineering | 04/2024 - Present

### National University of Computer and Engineering Sciences
Bachelor of Science, Computer Science | 06/2016 - 08/2020

## Projekte

### cv-tailor (LLM CV/Cover Tailoring + Application Management) ([portfolio](https://radheem.github.io/my-cv/projects/cv-tailor/))
- Entwicklung einer Python-CLI und eines **FastMCP Servers**, der die Anpassung von Lebenslauf und Anschreiben automatisiert (basierend auf unit-getesteter Projekt-Ranking-Logik mit Anthropic/Ollama) und vor Halluzinationen schützt.
- Entwicklung einer automatisierten **Gmail-Alert-Ingestion**-Pipeline (LinkedIn, Glassdoor, Indeed, Fraunhofer) sowie eines schlanken API-Fetching für Gastzugriffe.
- Sicherung von Dokumenten in Git durch clientseitige **AES-256-GCM**-Verschlüsselung, die über passwortgeschützte statische Seiten freigeschaltet wird.

### Information Retrieval System (IRS) - Distributed Systems Platform ([portfolio](https://radheem.github.io/my-cv/projects/irs/))
- Entwicklung von Go-Microservices mit gRPC und gRPC-Gateway auf Basis von Protobuf-first-APIs; Migration von Dapr zu nativem NATS JetStream (Messaging) und NATS KV (State).
- Integration von MCP (Model Context Protocol) zur Bereitstellung deklarativer, hot-reloadbarer Tools für LLM-Agenten über einen konfigurationsgetriebenen Toolbox-Server.
- Orchestrierung von best-effort ETL-Pipelines mit Hatchet in PostgreSQL und Dgraph; Validierung durch Ginkgo-E2E-Gates und Überwachung via OpenTelemetry-Distributed-Tracing.

## Kenntnisse

- Sprachen (gesprochen): Englisch (fließend), Deutsch (A2)
- Distributed Systems & Messaging: NATS (JetStream + KV), Kafka, gRPC, gRPC-Gateway, Hatchet, MCP (FastMCP), Dapr, OpenTelemetry
- Backend & API Architecture: Go, Python, TypeScript, NodeJS, NestJS, REST, API Design, System Design
- Cloud & Infrastructure: Kubernetes, kustomize, Skaffold, Cilium, external-dns, Docker, Helm, Terraform, AWS (EC2, RDS, DynamoDB)
- Databases & Storage: PostgreSQL (sqlc), MySQL, MongoDB/DocumentDB, Dgraph, DynamoDB, pgvector
- Web & Frontend: ReactJS, JavaScript, Bash, PHP
- ML/Data: Kubeflow Pipelines, KServe, scikit-learn, TensorFlow/Keras, pandas
