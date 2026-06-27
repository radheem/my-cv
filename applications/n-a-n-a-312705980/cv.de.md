---
tagline: "Senior Software Engineer"
---

## Berufserfahrung

### Al Hilal Invest — Senior Software Engineer
*Pakistan · 11/2023 – 03/2024*
- Entwickelte und dokumentierte neue Dienste und Funktionen, wodurch die Systemzuverlässigkeit und die Teamgeschwindigkeit verbessert wurden.
- Leitete System- und Code-Reviews und etablierte Best Practices für Architektur und Deployment.
- Modernisierte Deployment-Workflows durch die Dockerisierung von Backend-Diensten und die Optimierung von Release-Prozessen.

### Bluefin Exchange — Senior Software Engineer
*Pakistan · 06/2021 – 08/2023*
- Identifizierte und implementierte Verbesserungen im Systemdesign und schlug eigenständig skalierbare Lösungen für Kernservices vor.
- War als Systemexperte für Code- und Design-Reviews zuständig, betreute Junior-Entwickler und begleitete Projektinitiativen.
- Pflegte strenge Release-Prozesse und Dokumentation für Exchange-Services im großen Maßstab.

### Seed Labs — Software Engineer
*Pakistan · 06/2020 – 06/2021*
- Recherchierte und schlug technische Lösungen vor und lieferte robuste Implementierungen in funktionsübergreifenden Teams.
- Analysierte, bereinigte und visualisierte komplexe Datensätze, um umsetzbare Erkenntnisse für Stakeholder zu generieren.

## Ausbildung

### Technical University of Ilmenau
*Master of Research, Computer Systems and Engineering · 04/2024 – Present*

### National University of Computer and Engineering Sciences
*Bachelor of Science, Computer Science · 06/2016 – 08/2020*

## Projekte

- **IRS Platform (Stealth)** — Entwickelte eine auf Go basierende verteilte Plattform mit Protobuf-first gRPC-APIs, migrierte Legacy-Sidecars zu nativem NATS JetStream/KV für latenzarme Nachrichtenübertragung und Sitzungszustände und orchestrierte eine best-effort ETL-Pipeline nach PostgreSQL, Dgraph und DocumentDB über Hatchet mit Ginkgo-E2E-Datenqualitätsprüfung.
- **Second Brain (Document RAG)** — Implementierte eine fehlertolerante Dokumenten-Ingestion-Pipeline mit Hatchet unter Nutzung von pro-Schritt-Retries und Timeouts, streamte Echtzeit-Fortschritt über NATS JetStream + SSE und deployte lokale llama.cpp-Inferenz mit pgvector (HNSW)-Suche auf einem cloud-nativen k3d-Cluster mit cert-manager-TLS.
- **cv-tailor (LLM CV/Cover Tailoring + LinkedIn Automation)** — Entwickelte eine deterministische Python-Toolchain, die einen unit-getesteten Ranker nutzt, um faktische Projekt-/Skill-Daten vor der LLM-Textgenerierung zu fixieren, versioniert alle Bewerbungen in git mit einem MkDocs-geführten Lebenszyklus, verschlüsselt pro-Stelle-Dokumente im Browser und automatisiert die LinkedIn-Ingestion über containerisiertes Playwright mit Human-in-the-Loop-Review.

## Kenntnisse

- **Sprachen** — Englisch (fließend), Deutsch (A2)
- **Programmiersprachen** — Go, Python, SQL, TypeScript, JavaScript, Bash, PHP
- **Verteilte Systeme** — gRPC, NATS JetStream, NATS KV, Hatchet, Kafka, Dapr, MCP
- **Cloud-Native & Infrastruktur** — Kubernetes, kustomize, Skaffold, Helm, Cilium, Docker, Terraform, external-dns
- **Datenbanken & Persistenz** — PostgreSQL, MySQL, MongoDB/DocumentDB, Dgraph, DynamoDB, BigQuery, Snowflake, pgvector
