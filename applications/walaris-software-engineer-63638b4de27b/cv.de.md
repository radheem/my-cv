---
tagline: "Software Engineer"
---

## Berufserfahrung

### Al Hilal Invest - Senior Software Engineer
Pakistan | 11/2023 - 03/2024
- Backend-Dienste auf Kubernetes und AWS entworfen und containerisiert, Bereitstellungs-Pipelines für skalierbare Plattform-Infrastrukturen optimiert.
- Systemdesign und Code-Reviews geleitet, robuste Architekturmuster für verteilte Microservices und Cloud-Native-Deployments etabliert.
- Hochperformante Dienste mit NodeJS, TypeScript und Docker entwickelt und dokumentiert, zuverlässige Backend-Betriebssicherheit gewährleistet.

### Bluefin Exchange - Senior Software Engineer
Pakistan | 06/2021 - 08/2023
- OpenTelemetry, Prometheus und Grafana in verteilten Go/Python-Diensten integriert, um Systemdurchsatz zu überwachen und Latenzspitzen zu reduzieren.
- Systemdesign-Verbesserungen für Kern-Börsendienste identifiziert und implementiert, Infrastrukturzuverlässigkeit und Observability optimiert.
- Release-Prozesse gepflegt und Junior-Engineering-Teams geleitet, konsistente Deployment-Standards und Plattformstabilität gewährleistet.

### Seed Labs - Software Engineer
Pakistan | 06/2020 - 06/2021
- Machine-Learning-Modelle mit Python, TensorFlow und scikit-learn entwickelt und trainiert, Fokus auf datengetriebene prädiktive Lösungen.
- Komplexe Datensätze analysiert, bereinigt und visualisiert, um umsetzbare Erkenntnisse zu gewinnen, Entscheidungsfindung der Stakeholder und Modellvalidierung unterstützt.

## Ausbildung

### Technical University of Ilmenau
Master of Research, Computer Systems and Engineering | 04/2024 - Present

### National University of Computer and Engineering Sciences
Bachelor of Science, Computer Science | 06/2016 - 08/2020

## Projekte

### My Notebook (Document RAG) ([portfolio](https://radheem.github.io/my-cv/projects/my-notebook/))
- Dauerhafte, wiederholbare Dokumenten-Ingestion-Pipeline mit Hatchet (extract → chunk → embed → summarize → index) mit Timeout- und Retry-Steuerung pro Schritt sowie OpenTelemetry-Instrumentierung.
- Echtzeit-Fortschritts-Streaming über NATS JetStream + SSE, alle lokalen Inference-Prozesse gesichert über zwei llama.cpp-Server hinter einer OpenAI-kompatiblen API.
- Vektorsuche mit pgvector (HNSW, cosine) implementiert; cloud-nativ auf k3d mit cert-manager TLS und ExternalDNS deployed.

### cv-tailor (LLM CV/Cover Tailoring + Application Management) ([portfolio](https://radheem.github.io/my-cv/projects/cv-tailor/))
- Python-CLI und FastMCP-Server entwickelt, die CV/Anschreiben-Anpassung mit unit-getesteter Projekt-Ranking (Anthropic/Ollama) und Halluzinations-Schutz automatisieren.
- Automatisierte Gmail-Alert-Ingestion-Pipelines und bidirektionale Google-Sheets-Synchronisation entwickelt, um Lebenszyklen von Stellenbewerbungen zu verfolgen.
- Dokumente in Git mittels clientseitiger AES-256-GCM-Verschlüsselung gesichert, zugänglich über passwortgeschützte statische Pages.

### O-RAN AIML Framework ([portfolio](https://radheem.github.io/my-cv/projects/oran-aiml/))
- End-to-End-AIML-Framework auf Kubernetes mit Helm deployed, mit einem konfigurationsgetriebenen Python-SDK zur Automatisierung des vollständigen ML-Lebenszyklus (feature group → training → inference).
- Kubeflow-Training/Retraining-Pipelines (kfp) mit TensorFlow/Keras und scikit-learn erstellt, Modellserving über KServe mit integrierten Feature Stores und Artifact Storage.

## Kenntnisse

- Sprachen (gesprochen): Englisch (fließend), Deutsch (A2)
- KI/ML & MLOps: Kubeflow Pipelines, KServe, scikit-learn, TensorFlow/Keras, pandas, pgvector, vector-search, inference, model-training, agentic agents, LLM orchestration, RAG pipelines
- Cloud & Infrastruktur: Kubernetes, Helm, kustomize, Skaffold, Docker, Terraform, AWS (EC2, RDS, DynamoDB), Cilium, external-dns
- Systeme & Messaging: gRPC, NATS (JetStream + KV), Hatchet, MCP (FastMCP), Kafka, Dapr, OpenTelemetry, VictoriaMetrics, Grafana
- Datenbanken: PostgreSQL (sqlc), MySQL, MongoDB/DocumentDB, Dgraph, DynamoDB, BigQuery, Snowflake
- Programmiersprachen: Python, Go, SQL, TypeScript, JavaScript, Bash, PHP
- Web & Frameworks: ReactJS, NodeJS, NestJS, Django
