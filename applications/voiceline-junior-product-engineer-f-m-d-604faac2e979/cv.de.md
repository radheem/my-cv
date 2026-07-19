---
tagline: "Working Student Engineer / Full-Stack Developer"
---

## Berufserfahrung

### Al Hilal Invest - Senior Software Engineer
Pakistan | 11/2023 - 03/2024
- Entwickelte und containerisierte Backend-Dienste auf Kubernetes und AWS, optimierte Bereitstellungs-Pipelines für eine skalierbare Plattform-Infrastruktur.
- Leitete Systemdesign und Code-Reviews, etablierte robuste Architekturmuster für verteilte Microservices und cloud-native Bereitstellungen.
- Entwickelte und dokumentierte hochperformante Dienste mit NodeJS, TypeScript und Docker, um zuverlässigen Backend-Betrieb zu gewährleisten.

### Bluefin Exchange - Senior Software Engineer
Pakistan | 06/2021 - 08/2023
- Integrierte OpenTelemetry, Prometheus und Grafana in verteilte Go/Python-Dienste zur Überwachung der Systemdurchsatzleistung und zur Reduzierung von Latenzspitzen.
- Identifizierte und implementierte Systemdesign-Verbesserungen für Kernbörsendienste, optimierte die Zuverlässigkeit und Beobachtbarkeit der Infrastruktur.
- Pflegte Release-Prozesse und leitete Junior-Engineering-Teams, um konsistente Bereitstellungsstandards und Plattformstabilität zu gewährleisten.

### Seed Labs - Software Engineer
Pakistan | 06/2020 - 06/2021
- Entwickelte und trainierte Machine-Learning-Modelle mit Python, TensorFlow und scikit-learn, mit Fokus auf datengetriebene Vorhersagelösungen.
- Analysierte, bereinigte und visualisierte komplexe Datensätze, um umsetzbare Erkenntnisse zu gewinnen, und unterstützte damit die Entscheidungsfindung der Stakeholder sowie die Modellvalidierung.

## Ausbildung

### Technical University of Ilmenau
Master of Research, Computer Systems and Engineering | 04/2024 - Aktuell

### National University of Computer and Engineering Sciences
Bachelor of Science, Computer Science | 06/2016 - 08/2020

## Projekte

### My Notebook (Document RAG) ([portfolio](https://radheem.github.io/my-cv/projects/my-notebook/))
- Ausfallsichere, wiederholbare Dokumenten-Ingestion-Pipeline mit Hatchet (extract → chunk → embed → summarize → index) mit schrittweisen Timeouts, Wiederholungsmechanismen und OpenTelemetry-Instrumentierung.
- Echtzeit-Fortschritts-Streaming über NATS JetStream + SSE, wobei alle lokalen Inferenzen über zwei llama.cpp-Server hinter einer OpenAI-kompatiblen API gesichert sind.
- Vektorsuche implementiert mit pgvector (HNSW, cosine); cloud-native auf k3d bereitgestellt mit cert-manager TLS und ExternalDNS.

### cv-tailor (LLM CV/Cover Tailoring + Application Management) ([portfolio](https://radheem.github.io/my-cv/projects/cv-tailor/))
- Entwickelte eine Python-CLI und einen FastMCP-Server zur Automatisierung der CV/Anschreiben-Anpassung mit unit-getesteter Projekt-Ranking (Anthropic/Ollama) und Halluzionsfiltern.
- Entwickelte automatisierte Gmail-Alert-Ingestion-Pipelines und bidirektionale Google-Sheets-Synchronisation zur Verfolgung von Bewerbungslebenszyklen.
- Sicherte Dokumente in Git mittels clientseitiger AES-256-GCM-Verschlüsselung, die durch passwortgeschützte statische Pages geschützt wird.

### O-RAN AIML Framework ([portfolio](https://radheem.github.io/my-cv/projects/oran-aiml/))
- Bereitete ein End-to-End-AIML-Framework auf Kubernetes mit Helm, mit einem konfigurationsgetriebenen Python-SDK zur Automatisierung des vollständigen ML-Lebenszyklus (feature group → training → inference).
- Verfasste Kubeflow-Trainings-/Retraining-Pipelines (kfp) mit TensorFlow/Keras und scikit-learn, stellte Modelle über KServe bereit mit integrierten Feature Stores und Artifact Storage.

## Kenntnisse

- Sprachen (gesprochen): Englisch (fließend), Deutsch (A2)
- AI/ML & MLOps: Kubeflow Pipelines, KServe, scikit-learn, TensorFlow/Keras, pandas, pgvector, vector-search, inference, model-training, agentic agents, LLM orchestration, RAG pipelines
- Cloud & Infrastruktur: Kubernetes, Helm, kustomize, Skaffold, Docker, Terraform, AWS (EC2, RDS, DynamoDB), Cilium, external-dns
- Systeme & Messaging: gRPC, NATS (JetStream + KV), Hatchet, MCP (FastMCP), Kafka, Dapr, OpenTelemetry, VictoriaMetrics, Grafana
- Datenbanken: PostgreSQL (sqlc), MySQL, MongoDB/DocumentDB, Dgraph, DynamoDB, BigQuery, Snowflake
- Programmiersprachen: Python, Go, SQL, TypeScript, JavaScript, Bash, PHP
- Web & Frameworks: ReactJS, NodeJS, NestJS, Django
