# Curriculum Vitae

**Radheem Bin Razi**
Ilmenau, Germany | [sheikh.radheem@gmail.com](mailto:sheikh.radheem@gmail.com) | [portfolio](https://radheem.github.io/my-cv) | [linkedin](https://www.linkedin.com/in/radheem-razi) | [github](https://github.com/radheem)

[:material-download: Download CV (PDF)](assets/cv.pdf){ .md-button .md-button--primary download="Radheem-Bin-Razi-CV.pdf" }

## Summary
Software engineer with 5 years of experience across distributed systems, cloud-native platforms, and data-driven backends. Delivered microservices, event-driven pipelines, and ML infrastructure using Go, Python, and Kubernetes. Experienced in system design, documentation, and mentoring.

## Experience

### AiVader GmbH — Research Engineering Intern
*Germany · 02/2026 – 04/2026*

- Integrated and deployed a containerized 5G Standalone (SA) Open RAN testbed on a single host, combining pre-dockerized open-source applications (Open5GS 5GC, O-RAN SC Near-RT RIC, and srsRAN/OCUDU gNB) and establishing fully reproducible, runbook-configured deployments.
- Developed and integrated a custom xApp over the E2 interface to extract Key Performance Measurements (KPMs) from the gNB and publish them to a Kafka pub-sub message broker for downstream consumer applications.
- Stabilized and brought the containerized stack to operational readiness, configuring dual RF front-ends (ZeroMQ virtual RF and USRP B210 SDR band n78) and resolving PRACH collisions and CPU starvation under multi-UE load.
- Deployed and operated the O-RAN AI/ML Framework (AIMLFW) on Kubernetes (Kubeflow, KServe, Cassandra) to execute automated model-training and serving using the testbed's published KPM telemetry.
- Logged SRE troubleshooting runbooks to resolve VM cpu-scheduling, AVX2 SIGILL crashes, and network routing bugs.

### Al Hilal Invest — Senior Software Engineer
*Pakistan · 11/2023 – 03/2024*

- Owned new backend services end to end — design through documentation and release — as a senior individual contributor.
- Led system-design and code reviews, setting architectural direction and quality standards for the team.
- Drove improvements to deployment workflows and the containerization of backend services.

### Bluefin Exchange — Senior Software Engineer
*Pakistan · 06/2021 – 08/2023*

- Acted as system expert and design authority for a set of core exchange services, reviewing code and design decisions for correctness and scale.
- Independently identified system-design weaknesses and proposed, justified, and drove the solutions.
- Led and mentored teams of junior engineers across project initiatives.
- Owned release processes and technical documentation for multiple production services.

## Education

### Technical University of Ilmenau
*Master of Research, Computer Systems & Engineering · 04/2024 – Present*

### National University of Computer and Engineering Sciences
*Bachelor of Science, Computer Science · 06/2016 – 08/2020*

## Certifications
See the [Certifications](certificates.md) section for full syllabus details and verified PDF credentials:

- **Deep Learning Specialization** (*DeepLearning.AI via Coursera · January 2020*) — 5-course series covering feedforward networks, optimization, CNNs, RNNs, LSTMs, and Transformers.
- **Mathematics for Machine Learning: Linear Algebra** (*Imperial College London via Coursera · April 2022*) — Vector spaces, coordinate systems, matrices, eigenvalues, eigenvectors, and data projections (PCA).

## Projects
See the [Projects](projects/index.md) section for detailed write-ups:

- **[IRS Platform (Stealth)](projects/irs.md)** — distributed Go microservices, MCP integration & data pipelines.
- **[My Notebook](projects/my-notebook.md)** — self-hosted RAG document-intelligence service; durable Hatchet ingestion pipeline, local llama.cpp inference, pgvector semantic search & NATS JetStream progress streaming on a k3d homelab.
- **[cv-tailor](projects/cv-tailor.md)** — LLM CV/cover-letter tailoring and agentic job-hunting pipeline with a pure, unit-tested ranker (the LLM only writes prose, never invents facts); filesystem-first design cached in DuckDB, with automated Google Drive publishing, live Google Sheets status sync, and a containerized stop-before-submit Playwright LinkedIn flow.
- **[Gitpress](projects/gitpress.md)** — zero-server blog CMS; Google Docs as the content source, GitHub Actions build pipeline, GitHub Pages hosting & Google Apps Script for forms and analytics — no servers, no monthly bills.
- **[Homelab & Declarative Platform](projects/homelab.md)** — automated, single-node declarative homelab hosting CoreDNS, Tailscale/Headscale ingress, and self-healing local DNS routing.
- **[O-RAN AIML Framework](projects/oran-aiml.md)** — AI/ML platform for 5G networks with a Python client, Kubeflow pipelines & KServe serving (research, grade 1.0/A).
- **O-RAN / 5G SA Testbeds** — end-to-end 5G SA labs (gNB + Open5GS) with an integrated O-RAN Near-RT RIC and Grafana monitoring, in [Docker](projects/oran-testbed.md) (single-host, composable stacks, OCUDU gNB ZMQ/UHD, Kafka metrics pub/sub) and [Kubernetes](projects/5g-testbed.md) (Multus CNI, ONOS SDN, 50+ Mbps) variants — both featuring gNB, monitoring & O-RAN RIC.

## Skills
- **System & API Design** — microservices, event-driven, and contract-first architecture; schema design and evolution. *(gRPC, Protocol Buffers, REST, CUE)*
- **Distributed Systems** — messaging, durable state, and workflow orchestration with an emphasis on fault tolerance. *(NATS JetStream / KV, Hatchet, Kafka)*
- **Cloud-Native Deployment** — Kubernetes delivery, GitOps-style overlays, and CI/CD. *(Kubernetes, k3d, Helm, kustomize, Skaffold, Cilium, Docker, Terraform)*
- **Observability & Reliability** — metrics, logging, and distributed tracing; resilience and reboot recovery. *(OpenTelemetry, VictoriaMetrics, Prometheus, Grafana)*
- **Data & Persistence** — relational, document, graph, and time-series stores plus ingestion pipelines. *(PostgreSQL, MongoDB / DocumentDB, Dgraph, InfluxDB)*
- **AI / ML Integration** — LLM agent tooling and the ML lifecycle from training to serving. *(MCP, Kubeflow, KServe)*
- **Programming Languages** — Go, Python, TypeScript / JavaScript, PHP; ReactJS, NodeJS, NestJS, Django.
- **Languages** — English (fluent), German / Deutsch (A2).
- **Leadership** — system-design and code review, mentoring junior engineers, and technical documentation.

---

*References available upon request.*
