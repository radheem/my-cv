# Data Analyzer (BigQuery MCP)

An intelligent Model Context Protocol (MCP) and visualization pipeline for Google's public Political Ads transparency dataset.

## 🏛️ Architecture Overview

The system is split into two synchronized, high-performance services orchestrated via Docker Compose:

1. **Political Ads MCP Server**:
   - Python-based `FastMCP` application exposing specialized BigQuery tools.
   - Restricts LLM token usage by avoiding raw SQL spikes.
   - Automatically provisions a BigQuery datasource inside Grafana on boot.

2. **Official Grafana MCP Server**:
   - Runs alongside Grafana to provide standard MCP capabilities.
   - Automatically loads persistently provisioned Service Account Tokens.
   - Enables any MCP client to query, search, build, patch, and export visual Grafana dashboards dynamically.

## ⚙️ Tech Stack

- **Python 3.12+** with FastMCP
- **Google BigQuery**
- **Grafana**
- **Docker Compose**
