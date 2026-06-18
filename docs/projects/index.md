# Projects

Flagship projects spanning distributed backend systems, AI/ML platform engineering, and 5G / O-RAN network virtualization.

## :material-sitemap: Information Retrieval System (IRS) — Stealth Project
Go microservices ecosystem on native NATS (JetStream + KV) and direct gRPC, with an **MCP** integration for LLM agents, a per-user authenticated browser-session service, a vendor-adaptor contract, and a best-effort ETL pipeline into PostgreSQL (with DocumentDB cold archive). Deployed via Kubernetes, kustomize, Skaffold, and Cilium.

[:octicons-arrow-right-24: Read more](irs.md)

## :material-brain: Second Brain — Self-Hosted Document RAG
A personal **document-intelligence** service that ingests PDFs, articles, and notes through a durable **Hatchet** pipeline (extract → chunk → embed → summarize → index), then serves **semantic search and grounded RAG chat over your own documents** — running entirely on a **k3d homelab** with local `llama.cpp` inference (no cloud calls). Uses **pgvector** (HNSW) for similarity search and **NATS JetStream + SSE** for real-time ingestion progress. ([repo](https://github.com/radheem/my-notebook))

[:octicons-arrow-right-24: Read more](second-brain.md)

## :material-kubernetes: HA K3s Cluster Platform — k3d + Cilium L2
Fully automated, reboot-resilient high-availability K3s clusters in Docker (k3d), running **kube-proxy-free in eBPF mode** with **Cilium 1.18** as the sole CNI. Bare-metal `LoadBalancer` services via **L2 announcements + LB-IPAM**, a sequential-boot orchestrator for IP stability, a self-healing CNI fail-safe, self-managed CoreDNS, and Tailscale/Headscale ingress.

[:octicons-arrow-right-24: Read more](k3d.md)

## :material-home-assistant: Homelab — Declarative k8s with Zero-Touch LAN DNS
A declarative **k3d home lab** where deploying a `Service` + `HTTPRoute` with a `*.home.lan` hostname makes it reachable **by name with automatic HTTPS** from any LAN device — no manual DNS edits. **ExternalDNS** publishes records into an authoritative **CoreDNS** (etcd/skydns), a shared **Cilium Gateway** terminates a **cert-manager** wildcard cert, a selectable component stack adds monitoring/messaging/workflow/DB, and an optional in-cluster image registry lets you `docker push registry.home.lan/...` and have the nodes pull it. Single-node-focused — the deliberate trade-off vs the HA platform is no multi-node reboot resilience. ([live docs](https://radheem.github.io/home-lab/) · [repo](https://github.com/radheem/home-lab))

[:octicons-arrow-right-24: Read more](homelab.md)

## :material-robot: O-RAN AIML Framework — AI/ML Platform Engineering
End-to-end AI/ML framework for O-RAN compatible 5G networks on Kubernetes + Helm, driven by a custom **Python client/SDK**: feature management, model registry, Kubeflow training/retraining pipelines, and **KServe** model serving. Delivered as a 15-credit research project at TU Ilmenau (German grade 1.0 / A).

[:octicons-arrow-right-24: Read more](oran-aiml.md)

## :material-radio-tower: 5G srsRAN + O-RAN RIC Testbed (Docker)
Single-host Dockerized 5G SA lab: srsRAN gNB (ZMQ/UHD), Open5GS core, and an integrated **O-RAN SC Near-RT RIC** with Python **xApps** controlling the RAN over E2 (E2SM-KPM / RC / CCC), plus a Telegraf → InfluxDB → Grafana metrics pipeline. ([repo](https://github.com/radheemCorp/srsran-docker))

[:octicons-arrow-right-24: Read more](srsran-docker.md)

## :material-run-fast: Infinite Stickman — Arcade Runner
An endlessly scrolling monochrome arcade runner built with **Vanilla JS and HTML5 Canvas** — no framework, no build step, zero dependencies. Jump, double-jump, and duck under procedurally generated obstacles as the world gets faster. A global leaderboard is powered by **Google Sheets + Apps Script**: scores are submitted as a `text/plain` POST (no CORS preflight) and fetched as JSON — no backend to host. ([play](https://radheem.github.io/stickman/) · [repo](https://github.com/radheem/stickman))

[:octicons-arrow-right-24: Read more](stickman.md)

## :material-chart-bar: Sheet Dashboard — Google Sheets → Live Dashboard
A static, **zero-backend web app** that turns any link-shared Google Sheet into a live dashboard — instantly. Paste a Sheet link, select a data type, and the browser fetches the CSV directly from Google, parses it client-side, and renders KPI cards, six interactive charts, and a searchable, sortable table. No server, no sign-in, no build step. Built with an **extensible data-type registry** so new data sources (e.g. Google Analytics, Shopify) can be added by appending a single object. v1 targets Meta Ads analytics. ([live](https://radheem.github.io/csv-dashboard/) · [repo](https://github.com/radheem/csv-dashboard))

[:octicons-arrow-right-24: Read more](csv-dashboard.md)

## :material-newspaper-variant-outline: Gitpress — Zero-Server Blog on Google + GitHub
A static blog CMS with **no servers, no databases, and no hosting costs** — built entirely on **Google** (Docs, Sheets, Apps Script) and **GitHub** (Pages, Actions). Authors write posts in Google Docs; GitHub Actions pulls them via Google APIs, converts them to static HTML, and deploys to GitHub Pages. Visitor lead and feedback forms POST to a Google Apps Script web app that writes to Sheets and emails the owner. An optional admin dashboard reads live analytics from the same script. ([repo](https://github.com/radheem/gitpress))

[:octicons-arrow-right-24: Read more](gitpress.md)

## :material-server-network: 5G srsRAN Testbed — Network Virtualization (Kubernetes)
Kubernetes-orchestrated end-to-end 5G testbed (srsRAN + Open5GS) with **Multus CNI** multi-homed networking (N2/N3/N6), ZeroMQ virtual RF, host-based UEs, an integrated **O-RAN Near-RT RIC** over E2, an **ONOS SDN** transport network, and Prometheus/Grafana. Achieved 50+ Mbps TCP throughput. ([repo](https://github.com/radheemCorp/srsRAN-dep-zmq))

[:octicons-arrow-right-24: Read more](5g-testbed.md)
