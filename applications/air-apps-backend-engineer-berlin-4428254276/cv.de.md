---
tagline: "Backend Engineer"
---

## Berufserfahrung

### Al Hilal Invest — Senior Software Engineer
*Pakistan · 11/2023 – 03/2024*
- Entwickelte und dokumentierte Backend-Services und Features mit NodeJS, TypeScript und ReactJS, optimierte Bereitstellungsprozesse und containerisierte Backend-Services auf AWS EC2 und S3.
- Leitete Systemdesign und Code-Reviews, um Clean-Code-Praktiken und architektonische Integrität im Team durchzusetzen.
- Optimierte Bereitstellungsprozesse und containerisierte Backend-Services, wobei MySQL und MongoDB für die Datenspeicherung genutzt wurden.

### Bluefin Exchange — Senior Software Engineer
*Pakistan · 06/2021 – 08/2023*
- Identifizierte Optimierungspotenziale im Systemdesign und schlug Lösungen für Börsendienste mit NodeJS, Go und TypeScript vor.
- Überprüfte Code und Designentscheidungen als Systemexperte, betreute Junior-Entwickler und leitete Teams bei Projektinitiativen.
- Pflegte Release-Prozesse und Dokumentation, wobei PostgreSQL, DynamoDB, Kafka und Terraform für cloud-native Infrastruktur genutzt wurden.

### Seed Labs — Software Engineer
*Pakistan · 06/2020 – 06/2021*
- Recherchierte Lösungen und schlug Implementierungsdesigns mit NodeJS und Python vor.
- Lieferte in dreiköpfigen Teams unter Mentoring Lösungen ein, analysierte, bereinigte und visualisierte Daten, um Stakeholdern Erkenntnisse zu präsentieren.
- Analysierte, bereinigte und visualisierte Daten zur Präsentation von Erkenntnissen für Stakeholder, wobei AWS EC2, MongoDB und MySQL genutzt wurden.

## Ausbildung

### Technical University of Ilmenau
*Master of Research, Computer Systems and Engineering · 04/2024 – Heute*

### National University of Computer and Engineering Sciences
*Bachelor of Science, Computer Science · 06/2016 – 08/2020*

## Projekte

- **IRS Platform (Stealth)** — Entwickelte Go-Mikroservices mit gRPC und gRPC-Gateway unter Verwendung von Protobuf-first-APIs, migrierte von Dapr zu nativem NATS JetStream für Messaging und Session-State, während best-effort ETL-Pipelines nach PostgreSQL (sqlc), Dgraph und DocumentDB über Hatchet mit deklarativem Routing und Ginkgo E2E-Datenqualitäts-Gates orchestriert wurden. Sicherte pro-Nutzer-Browsersitzungen mit Playwright, Gateway-Consistent-Hashing und einem AES-256-GCM-Credential-Vault, bereitgestellt auf Kubernetes mit kustomize, Skaffold und Cilium.
- **cv-tailor (LLM CV/Cover Tailoring + LinkedIn Automation)** — Entwickelte eine Python-basierte Anwendung mit einem unit-getesteten Ranker und LLM-Integration, versionierte jede Bewerbung in Git mit einer Statuslebensdauer, die auf einer MkDocs-Site angezeigt wird. Implementierte ein robustes CI/CD mit GitHub Actions zum Rendern, Signieren und Bereitstellen auf GitHub Pages, schützte pro-Stelle Dokumente mit in-Browser-PBKDF2- und AES-256-GCM-Verschlüsselung und stellte sicher, dass keine API-Keys im CI verwendet wurden. Fügte einen containerisierten LinkedIn-Ingestion-Flow über Playwright mit menschlich getakteter Automatisierung und VNC-CAPTCHA-Handover hinzu, der reproduzierbare Ausgaben mit Model/Seed/Prompt-Hash-Manifests generiert, die durch Quality-Benchmark-Regression-Gates geschützt sind.
- **O-RAN Testbed (Open5GS + RIC + OCUDU gNB)** — Konsolidierte ein 5G-SA-Testbed in zusammensetzbaren Docker-Compose-Stacks für Core, gNB, RIC und Monitoring, wodurch remote gNB-Attachments über geteilte Bridge-Netzwerke ermöglicht wurden. Entwickelte eine Kafka-Metriken-Pub/Sub-Pipeline, in der xApps per-UE-KPM-Daten an Kafka veröffentlichen, wobei Consumer Nachrichten an InfluxDB 3 (Grafana), MongoDB und ein AIMLFW-kompatibles InfluxDB 2 weiterleiten. Integrierte den O-RAN SC Near-RT RIC über E2 mit Python-xApps unter Verwendung von E2SM-KPM, E2SM-RC und E2SM-CCC, wobei die gNB auf OCUDU CU/DU mit einem einheitlichen Image für ZMQ-virtual-RF und UHD over-the-air auf USRP B210 SDR lief.

## Kenntnisse

- **Sprachen** — Englisch (fließend), Deutsch (A2)
- **Programmiersprachen** — TypeScript, Go, Python, SQL, JavaScript, Bash, PHP
- **Cloud-Native & Infrastruktur** — Kubernetes, kustomize, Skaffold, Helm, Cilium, Docker, Terraform, external-dns
- **Web & API** — NodeJS, REST, ReactJS, NestJS, Django, Protocol Buffers, OpenAPI
- **Datenbanken & Persistenz** — PostgreSQL, MySQL, MongoDB/DocumentDB, Dgraph, DynamoDB, BigQuery, Snowflake, pgvector
