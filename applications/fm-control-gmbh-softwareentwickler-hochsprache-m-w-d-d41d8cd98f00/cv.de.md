---
tagline: "Softwareentwickler (Hochsprache) / Software Developer"
---

## Berufserfahrung

### AiVader GmbH - Research Engineering Intern
Germany | 02/2026 - 04/2026
- Containerisierung und Bereitstellung eines Full-Stack-5G-Testbeds mit Docker Compose, Integration von Open5GS 5GC, O-RAN SC RIC sowie srsRAN/OCUDU gNB-Komponenten.
- Aufbau der Kafka-to-InfluxDB-MongoDB Fan-Out-Datenpipeline sowie Grafana-Dashboards zur Echtzeit-KPM-Visualisierung.
- Tech: Docker, Docker Compose, Kafka, InfluxDB, Grafana, Python, Kubernetes, Linux, C++.

### Al Hilal Invest - Senior Software Engineer
Pakistan | 11/2023 - 03/2024
- Entwicklung und Release von Fullstack-Features mit ReactJS, NodeJS, TypeScript, NestJS und PHP, Anbindung der UI über REST APIs an MySQL und MongoDB.
- Containerisierung von Backend-Services sowie Optimierung der Deployment-Pipelines auf AWS EC2 und Kubernetes.
- Leitung des Systemdesigns und von Code Reviews in Frontend- und Backend-Teams.

### Bluefin Exchange - Senior Software Engineer
Pakistan | 06/2021 - 08/2023
- Aufbau und Wartung von ReactJS-Frontend und NodeJS/Go-Backend-Services für eine High-Throughput-Trading-Plattform.
- Integration von OpenTelemetry, Prometheus und Grafana zur Überwachung der Engine-Durchsatzleistung und des Kafka-Consumer-Lags.
- Mentoring von Junior-Engineers sowie Koordination der Releases für Frontend- und Backend-Teams.

## Ausbildung

### Technical University of Ilmenau
Master of Research, Computer Systems and Engineering | 04/2024 - Present

### National University of Computer and Engineering Sciences
Bachelor of Science, Computer Science | 06/2016 - 08/2020

## Projekte

### My Notebook (Document RAG) ([portfolio](https://radheem.github.io/my-cv/projects/my-notebook/))
- Aufbau und Release einer Fullstack-RAG-Anwendung: FastAPI-Backend (Python) mit Next.js-Frontend für Dokument-Upload, semantische Suche und Chat.
- Entwurf einer robusten, wiederholbaren Ingestion-Pipeline (Hatchet → extract → chunk → embed → summarize → index) mit Fortschritts-Streaming über NATS JetStream + SSE.
- Implementierung von pgvector (HNSW, cosine) für semantische Suche; alle Inference-Aufrufe werden privat von llama.cpp bereitgestellt.

### cv-tailor (LLM CV/Cover Tailoring) ([portfolio](https://radheem.github.io/my-cv/projects/cv-tailor/))
- Entwicklung einer Python-CLI und eines FastMCP-Servers zur Automatisierung der CV/Cover-Letter-Anpassung mit unit-getesteter Projekt-Ranking (Anthropic/Ollama).
- Entwicklung automatisierter Gmail-Alert-Ingestion-Pipelines (LinkedIn, Glassdoor, Indeed) sowie bidirektionaler Google-Sheets-Lebenszyklus-Verfolgung.
- Integration von MkDocs Material Static Site, GitHub Actions CI/CD sowie clientseitiger AES-256-GCM-Dokumentverschlüsselung.

### Sheet Dashboard ([portfolio](https://radheem.github.io/my-cv/projects/csv-dashboard/))
- Aufbau einer Zero-Backend-Web-App, die beliebige Google Sheets in ein Live-Dashboard mit clientseitiger CSV-Parserung, KPI-Cards und Diagrammen umwandelt.
- Implementierung eines erweiterbaren Datentyp-Registries und Diagramm-Komponenten ausschließlich in Vanilla JavaScript.

## Kenntnisse

- Sprachen: Englisch (fließend), Deutsch (A2)
- Frontend: ReactJS, Next.js, TypeScript, JavaScript, Vanilla JS, HTML5, CSS
- Backend: Go, Python, NodeJS, NestJS, Django, FastAPI, REST, gRPC
- Datenbanken: PostgreSQL (sqlc), MySQL, MongoDB/DocumentDB, Dgraph, DynamoDB, BigQuery, Snowflake, pgvector
- Cloud/Infra: Kubernetes, Docker, Helm, kustomize, Skaffold, CI/CD (GitHub Actions), Terraform, AWS (EC2, S3)
- Messaging & Observability: NATS (JetStream + KV), Kafka, OpenTelemetry, Prometheus, VictoriaMetrics, Grafana
- ML/Data: Kubeflow, KServe, scikit-learn, TensorFlow/Keras, pandas
- Programmiersprachen: Go, Python, SQL, TypeScript, JavaScript, Bash, PHP
