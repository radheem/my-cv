---
search:
  exclude: true
tagline: Senior platform engineer building agentic developer tooling — MCP servers, LLM integrations, and the guardrails that make AI adoption safe
---

## Experience

### Bluefin Exchange — Senior Software Engineer
*Pakistan · 06/2021 – 08/2023*

- Acted as design authority and system expert for the core services of a high-throughput crypto exchange, reviewing code and design decisions across teams in a regulated, high-volume fintech environment.
- Independently identified system-design improvements rather than waiting for scoped tickets — surfacing bottlenecks and driving fixes with engineering buy-in.
- Maintained release processes and documentation engineers actually used, and led/mentored teams of junior engineers through hands-on presence.

### Al Hilal Invest — Senior Software Engineer
*Pakistan · 11/2023 – 03/2024*

- Built and documented new backend services and features for a fintech product, leading system-design and code reviews.
- Improved deployment processes and dockerized backend services, removing friction from delivery workflows.

### Seed Labs — Software Engineer
*Pakistan · 06/2020 – 06/2021*

- Researched and proposed designs in small teams, then analyzed, cleaned, and visualized data to give stakeholders a coherent view for decisions.

## Education

### Technical University of Ilmenau
*Master of Research, Computer Systems & Engineering · 04/2024 – Present*

### National University of Computer and Engineering Sciences
*Bachelor of Science, Computer Science · 06/2016 – 08/2020*

## Projects

- **IRS Platform (Stealth)** — Distributed Go microservices (gRPC/Protobuf, NATS JetStream) with MCP tooling that exposes the platform to LLM agents, and a per-user browser-session service secured by an AES-256-GCM vault; deployed on Kubernetes (kustomize, Skaffold, Cilium).
- **cv-tailor (LLM tooling with guardrails)** — Python tool where a pure, unit-tested ranker makes the decisions and the LLM only writes prose (no fabrication); integrates GitHub Actions and git as the tracking system, behind an AES-256-GCM gate — an applied example of weighing AI productivity gains against safety constraints.
- **Second Brain (Document RAG)** — Self-hosted document-intelligence service with durable, retryable ingestion, local llama.cpp inference (OpenAI-compatible), pgvector semantic search, and SSE progress streaming; cloud-native on k3d.

## Skills

- **Languages** — English (fluent), Deutsch (A2)
- **Programming Languages** — Python, Go, TypeScript, JavaScript, SQL, Bash, PHP
- **AI / Agentic Tooling** — MCP, Claude/LLM model integrations, llama.cpp, pgvector, Kubeflow, KServe
- **Cloud-Native & Integrations** — Kubernetes, Docker, gRPC, NATS JetStream, Kafka, Hatchet, Terraform, GitHub Actions / CI-CD
- **Observability & Reliability** — OpenTelemetry, Prometheus, Grafana, VictoriaMetrics
