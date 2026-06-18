# Gitpress — Zero-Server Blog on Google + GitHub

A static blog CMS with **no servers, no databases, and no monthly bills** — built entirely on two platforms most people already know and trust: **Google** (Docs, Sheets, Apps Script) and **GitHub** (Pages, Actions). Write posts in Google Docs like you would any document; the rest is automatic.

!!! abstract "At a glance"
    **Role**: Full-stack engineer (solo) &nbsp;·&nbsp; **Stack**: Node.js build pipeline · Google APIs (Drive, Docs, Sheets, Apps Script) · GitHub Actions · GitHub Pages · Tailwind CSS &nbsp;·&nbsp; **Hosting cost**: $0

    **Repo**: [github.com/johndoe/gitpress](https://github.com/johndoe/gitpress) &nbsp;·&nbsp; **Example**: [johndoe.github.io/github-blogs](https://johndoe.github.io/github-blogs/) &nbsp;·&nbsp; **Template**: deploy your own blog in minutes — no server required

## Architecture

The system has **no backend process** — only static files on GitHub Pages and Google's always-free, serverless infrastructure. The author's laptop never even needs to run a build; GitHub Actions handles everything.

```mermaid
flowchart LR
  AUTHOR([Author])
  VISITOR([Visitor])
  ADMIN([Admin])

  subgraph google[Google — free tier]
    GD["Google Drive\n📄 Docs folder\n(post bodies)"]
    GS["Google Sheets\n🗂 Blog Index\n(slug · status · tags)"]
    GAS["Google Apps Script\nWeb App /exec\n(forms + dashboard API)"]
  end

  subgraph github[GitHub — free tier]
    REPO["Repository\n(source + templates)"]
    GA["GitHub Actions\nbuild + deploy"]
    GP["GitHub Pages\nstatic site"]
  end

  AUTHOR -->|"writes posts\n(WYSIWYG)"| GD
  AUTHOR -->|"sets status = published"| GS
  GS -.->|"optional: webhook\non status change"| REPO
  REPO -->|"push / daily cron / manual"| GA
  GA -->|"read published rows"| GS
  GA -->|"fetch Docs + images"| GD
  GA -->|"deploy static HTML"| GP

  VISITOR -->|"reads blog"| GP
  VISITOR -->|"submits form"| GAS
  GAS -->|"appends row"| GS
  GAS -->|"emails owner"| AUTHOR

  ADMIN -->|"GET with token"| GAS
  GAS -->|"JSON: leads + feedback"| ADMIN
```

## Highlights
- Built a **constraint-driven, zero-server CMS** — no databases, no backend processes, no hosting costs. The entire system is stitched from two free platforms (Google, GitHub) with a Node.js build script as the only glue.
- Used **Google Docs as the content source** — authors write in a familiar WYSIWYG editor with real-time collaboration, footnotes, images, and offline support; no Markdown, no proprietary CMS.
- Designed a **Google Sheets + Apps Script backend** for dynamic functionality (lead capture, feedback forms, admin dashboard) on a static site — forms POST directly to Apps Script, which writes to Sheets and emails the owner on new leads, all without a server.
- Built **incremental builds** with a file-based cache: each Doc's `modifiedTime` is stored, so unchanged posts and already-downloaded images are skipped — keeping CI fast regardless of blog size.
- Implemented a **Google Docs → sanitized HTML converter** that handles formatted text, headings, tables, nested lists, embedded images (downloaded and self-hosted), and Drive-hosted video embeds via a custom `[[media: filename]]` syntax.
- Wired **four GitHub Actions triggers** — push, daily cron, manual dispatch, and a repository-dispatch webhook (callable from Apps Script when a post's status changes) — giving the author a choice between instant and scheduled publishing.
- Built a **password-gated admin dashboard** (Chart.js KPI cards, lead tables, feedback summaries) that reads live data from Apps Script with a read token and falls back to static JSON snapshots if the endpoint is unreachable.

## How It Works

### Publishing a post

```mermaid
sequenceDiagram
  actor Author
  participant GS as Google Sheets<br/>(Blog Index)
  participant GAS as Google Apps Script
  participant GA as GitHub Actions
  participant GD as Google Drive / Docs
  participant GP as GitHub Pages

  Author->>GS: set status = published
  GS-->>GAS: (optional) on-edit trigger
  GAS->>GA: POST repository_dispatch event
  activate GA
  GA->>GS: fetch all published rows
  GA->>GD: fetch each Doc (structured JSON)
  GD-->>GA: content + image URLs
  GA->>GA: convert Docs → HTML<br/>download & self-host images<br/>render templates (Tailwind)
  GA->>GP: deploy static site artifact
  deactivate GA
  GP-->>Author: live at johndoe.github.io/...
```

### Visitor form + admin dashboard

```mermaid
sequenceDiagram
  actor Visitor
  actor Admin
  participant GP as GitHub Pages<br/>(static HTML)
  participant GAS as Google Apps Script
  participant GS as Google Sheets

  Visitor->>GP: load blog post
  GP-->>Visitor: static HTML — no server roundtrip
  Visitor->>GAS: POST lead / feedback form
  GAS->>GS: append row
  GAS-->>Visitor: 200 OK
  GAS->>Admin: email — new lead notification

  Admin->>GP: open /admin/dashboard
  GP-->>Admin: login page (SHA-256 gate)
  Admin->>GAS: GET ?token=READ_TOKEN
  GAS->>GS: read leads + feedback
  GS-->>GAS: rows
  GAS-->>Admin: JSON
  Admin->>Admin: render KPI cards + Chart.js graphs
```

## Build Pipeline
The Node.js build runs entirely inside GitHub Actions via a **Google service-account key** stored as a GitHub Secret — no credentials ever touch the repository. Steps:

1. Authenticate with a service-account key (`GOOGLE_SA_KEY`) and initialize Drive, Docs, and Sheets API clients.
2. Read the Blog Index Sheet; filter rows where `status = published` and `publish_date ≤ today`.
3. For each post, check the cache (`modifiedTime` manifest) — skip if unchanged.
4. Fetch the Doc's structured JSON; extract text blocks, images, and formatting.
5. Download and self-host all images; resolve `[[media: filename]]` Drive-video embeds.
6. Sanitize the HTML (allowlist: headings, links, tables, code, iframes from Drive).
7. Render home, blog-index, and post-detail pages from HTML templates with Tailwind.
8. Upload the site artifact; GitHub Pages deploys it.

## Tech Stack
`Node.js 20` · `Google Drive API v3` · `Google Docs API v1` · `Google Sheets API v4` · `Google Apps Script` · `GitHub Actions` · `GitHub Pages` · `Tailwind CSS (CDN)` · `Chart.js` · `sanitize-html` · `marked`

!!! note "Design trade-offs"
    The admin login is a client-side SHA-256 gate — transparent about its limits and suitable for personal use. The README explicitly documents when to upgrade (Cloudflare Access, Supabase) for stricter access control. The `READ_TOKEN` is intentionally scoped to read-only dashboard data.
