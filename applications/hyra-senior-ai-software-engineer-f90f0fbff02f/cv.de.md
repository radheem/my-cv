---
tagline: "Senior Full-Stack Engineer"
---

## Berufserfahrung

### Al Hilal Invest - Senior Software Engineer
Pakistan | 11/2023 - 03/2024
- Architektierte und containerisierte Backend-Services auf Kubernetes und AWS, optimierte Bereitstellungs-Pipelines für skalierbare Plattform-Infrastruktur.
- Leitete Systemdesign und Code-Reviews, etablierte robuste Architekturmuster für verteilte Microservices und Cloud-Native-Deployments.
- Entwickelte und dokumentierte hochperformante Services mit NodeJS, TypeScript und Docker, sicherte zuverlässige Backend-Operationen.

### Bluefin Exchange - Senior Software Engineer
Pakistan | 06/2021 - 08/2023
- Integrierte OpenTelemetry, Prometheus und Grafana in verteilte Go/Python-Services zur Überwachung der Systemdurchsatzleistung und Reduzierung von Latenzspitzen.
- Identifizierte und implementierte Systemdesign-Verbesserungen für Core-Börsenservices, optimierte Infrastrukturzuverlässigkeit und Observability.
- Wartete Release-Prozesse und leitete Junior-Engineering-Teams, sicherte konsistente Deployment-Standards und Plattformstabilität.

### Seed Labs - Software Engineer
Pakistan | 06/2020 - 06/2021
- Entwickelte und trainierte Machine-Learning-Modelle mit Python, TensorFlow und scikit-learn, mit Fokus auf datengetriebene prädiktive Lösungen.
- Analysierte, bereinigte und visualisierte komplexe Datensätze, um umsetzbare Erkenntnisse zu gewinnen, und unterstützte Stakeholder-Entscheidungen sowie Modellvalidierung.

## Ausbildung

### Technical University of Ilmenau
Master of Research, Computer Systems and Engineering | 04/2024 - Present

### National University of Computer and Engineering Sciences
Bachelor of Science, Computer Science | 06/2016 - 08/2020

## Projekte

### My Notebook (Document RAG) ([portfolio](https://radheem.github.io/my-cv/projects/my-notebook/))
- Dauerhafte, wiederholbare Dokument-Ingestion-Pipeline mit Hatchet (extract → chunk → embed → summarize → index) mit Timeout- und Retry-Steuerung pro Schritt sowie OpenTelemetry-Instrumentierung.
- Echtzeit-Fortschritts-Streaming über NATS JetStream + SSE, wobei alle lokalen Inferenzen über zwei llama.cpp-Server hinter einer OpenAI-kompatiblen API gesichert sind.
- Vektorsuche implementiert mit pgvector (HNSW, cosine); Cloud-Native-Deployment auf k3d mit cert-manager TLS und ExternalDNS.

### cv-tailor (LLM CV/Cover Tailoring + Application Management) ([portfolio](https://radheem.github.io/my-cv/projects/cv-tailor/))
- Entwickelte eine Python-CLI und einen FastMCP-Server zur Automatisierung der CV/Cover-Letter-Anpassung mit unit-getesteter Projekt-Ranking (Anthropic/Ollama) und Halluzinations-Schutz.
- Entwickelte automatisierte Gmail-Alert-Ingestion-Pipelines und bidirektionale Google-Sheets-Synchronisation zur Verfolgung von Bewerbungslebenszyklen.
- Sicherte Dokumente in Git mittels clientseitiger AES-256-GCM-Verschlüsselung, geschützt durch passwortgeschützte statische Pages.

### O-RAN AIML Framework ([portfolio](https://radheem.github.io/my-cv/projects/oran-aiml/))
- Deployte ein End-to-End-AIML-Framework auf Kubernetes mit Helm, mit einem konfigurationsgetriebenen Python-SDK zur Automatisierung des vollständigen ML-Lebenszyklus (feature group → training → inference).
- Erstellte Kubeflow-Trainings-/Retraining-Pipelines (kfp) mit TensorFlow/Keras und scikit-learn, bereitstellte Modelle über KServe mit integrierten Feature Stores und Artifact Storage.

## Kenntnisse

- Sprachen (gesprochen): Englisch (fließend), Deutsch (A2)
- AI/ML & MLOps: Kubeflow Pipelines, KServe, scikit-learn, TensorFlow/Keras, pandas, pgvector, vector-search, inference, model-training, agentic agents, LLM orchestration, RAG pipelines
- Cloud & Infrastruktur: Kubernetes, Helm, kustomize, Skaffold, Docker, Terraform, AWS (EC2, RDS, DynamoDB), Cilium, external-dns
- Systeme & Messaging: gRPC, NATS (JetStream + KV), Hatchet, MCP (FastMCP), Kafka, Dapr, OpenTelemetry, VictoriaMetrics, Grafana
- Datenbanken: PostgreSQL (sqlc), MySQL, MongoDB/DocumentDB, Dgraph, DynamoDB, BigQuery, Snowflake
- Programmiersprachen: Python, Go, SQL, TypeScript, JavaScript, Bash, PHP
- Web & Frameworks: ReactJS, NodeJS, NestJS, Django
