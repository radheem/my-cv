# cv-tailor — developer & application workflow.
# Run `make` (or `make help`) for the target list.
#
# Conventions:
#   * The project is uv-managed and all commands run through `uv run`.
#   * PDFs are rendered with LaTeX (latex/*.cls) via scripts/build-application.sh
#     (local latexmk, else the texlive/texlive Docker image).
#
# Common overridable variables (make VAR=value target):
#   SOURCE   job posting URL or .txt/.md path     (required by `new`)
#   ID       numeric job id or full slug            (translate/pdf/upload/status/archive)
#   RECIPIENT cover-letter salutation name         (new)
#   PROVIDER  anthropic | ollama                   (new/translate)
#   MODEL     model id override                    (new/translate)
#   OLLAMA_URL OpenAI-compatible base URL          (new/translate)
#   STATUS / ID  lifecycle update                  (status)
#   PORT     dev server port (default 8000)

UV_RUN  := uv run
PORT    ?= 8000

.DEFAULT_GOAL := help

# ---- Help ------------------------------------------------------------------

.PHONY: help
help: ## Show this help
	@echo "cv-tailor — make targets:\n"
	@grep -hE '^[a-zA-Z0-9_-]+:.*## ' $(MAKEFILE_LIST) \
	  | awk 'BEGIN{FS=":.*## "}{printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'
	@echo "\nExamples:"
	@echo "  make install-all"
	@echo "  make new SOURCE=path/to/job.txt --provider anthropic"
	@echo "  make new SOURCE=jd.txt PROVIDER=ollama OLLAMA_URL=http://host:11434/v1 MODEL=qwen3.6-35b"
	@echo "  make preview            # build the gated site and serve it"
	@echo "  make status ID=4427480993 STATUS=applied"

# ---- Setup -----------------------------------------------------------------

.PHONY: install
install: ## Install base deps (site build + gate; no API key)
	uv sync

.PHONY: install-generate
install-generate: ## Install generation deps (Anthropic API + URL fetch)
	uv sync --extra generate --extra fetch

.PHONY: install-ollama
install-ollama: ## Install local Ollama / OpenAI-compatible backend
	uv sync --extra ollama

.PHONY: install-dev
install-dev: ## Install dev deps (pytest)
	uv sync --extra dev

.PHONY: install-all
install-all: ## Install everything (base + generate + fetch + ollama + dev)
	uv sync --all-extras

.PHONY: install-screenshot
install-screenshot: ## Install screenshot capture deps (PixelRAG render + openai)
	uv sync --extra screenshot
	@echo "Next: ollama pull qwen3-vl:8b   (on genai.ltc.hsnet)"

.PHONY: playwright
playwright: ## Install the Playwright Chromium browser (needed to fetch job URLs)
	$(UV_RUN) playwright install chromium

# ---- LinkedIn ingest (Sprint 1) --------------------------------------------

KEYWORDS ?= platform engineer
LIMIT    ?= 5

# Run containers as the invoking host user so vault/ files match host ownership.
# (bash's $UID is readonly and not exported, so Compose can't see it — use our own vars.)
DOCKER_UID := $(shell id -u)
DOCKER_GID := $(shell id -g)
export DOCKER_UID DOCKER_GID

.PHONY: ingest
ingest: ## Run a single ad-hoc search inside the ingest container: make ingest KEYWORDS="..." [LOCATION= GEO_ID= DISTANCE= LIMIT= DAYS=7 MAX_APPLICANTS=100 EASY_APPLY=1]
	docker compose run --rm --service-ports ingest cv-tailor ingest \
	  --keywords "$(KEYWORDS)" $(if $(LOCATION),--location "$(LOCATION)") --limit $(LIMIT) \
	  $(if $(GEO_ID),--geo-id "$(GEO_ID)") $(if $(DISTANCE),--distance "$(DISTANCE)") \
	  $(if $(DAYS),--days "$(DAYS)") $(if $(MAX_APPLICANTS),--max-applicants "$(MAX_APPLICANTS)") \
	  $(if $(EASY_APPLY),--easy-apply)

.PHONY: hunt
hunt: ## Run every search in config/search.yml inside the ingest container
	docker compose run --rm --service-ports ingest cv-tailor hunt

.PHONY: capture
capture: ## Capture ONE job link inside the ingest container: make capture URL="https://www.linkedin.com/jobs/view/<id>"
	@test -n "$(URL)" || { echo 'URL required, e.g. make capture URL="https://www.linkedin.com/jobs/view/123"'; exit 2; }
	docker compose run --rm --service-ports ingest cv-tailor capture "$(URL)"

VISION_MODEL ?= qwen3-vl:32b

.PHONY: screenshot
screenshot: ## Capture a job posting via screenshot + Ollama vision (no session) in-container: make screenshot SOURCE=<url-or-file>
	@test -n "$(SOURCE)" || { echo 'SOURCE required, e.g. make screenshot SOURCE="https://example.com/jobs/123"'; exit 2; }
	docker compose run --rm ingest cv-tailor screenshot "$(SOURCE)" --vision-model "$(VISION_MODEL)"

DAYS    ?= 7
MAX_APPLICANTS ?= 100
TOP     ?= 10

.PHONY: job-hunt
job-hunt: ## Full pipeline inside the ingest container: search 4 cities → score → generate top N → PDF → Drive → push
	docker compose run --rm ingest bash scripts/job-hunt.sh --top $(TOP)

.PHONY: job-hunt-dry
job-hunt-dry: ## Dry run inside the ingest container: show what job-hunt would do without running anything
	docker compose run --rm ingest bash scripts/job-hunt.sh --top $(TOP) --dry-run

FILTER  ?= "linkedin job alert"
LIMIT   ?= 10
ORDER   ?= top

.PHONY: gmail-hunt
gmail-hunt: ## Search Gmail for alerts inside the ingest container, capture, and generate applications: make gmail-hunt [FILTER="..."] [LIMIT=10] [ORDER=top|fifo]
	docker compose run --rm ingest bash scripts/gmail-hunt.sh --filter "$(FILTER)" --limit $(LIMIT) --order $(ORDER)

.PHONY: score
score: ## Score captured JDs and print ranking: make score [TOP=10]
	$(UV_RUN) python3 scripts/score-jds.py --top $(TOP)

.PHONY: docker-build
docker-build: ## Build the ingest container image
	docker compose build

.PHONY: docker-ingest
docker-ingest: ## Run a single ad-hoc search in the container: make docker-ingest KEYWORDS="..." [LOCATION= GEO_ID= LIMIT=]
	docker compose run --rm --service-ports ingest cv-tailor ingest \
	  --keywords "$(KEYWORDS)" $(if $(LOCATION),--location "$(LOCATION)") \
	  $(if $(GEO_ID),--geo-id "$(GEO_ID)") --limit $(LIMIT)

.PHONY: docker-hunt
docker-hunt: ## Run every search in config/search.yml in the container (config mounted at runtime)
	docker compose run --rm --service-ports ingest cv-tailor hunt

.PHONY: docker-login
docker-login: ## First-time VNC login (long timeout to solve CAPTCHA): VNC_BIND=<ip> VNC_PASSWORD=<pw> make docker-login
	docker compose run --rm --service-ports \
	  -e LINKEDIN_CHALLENGE_TIMEOUT=$(or $(CHALLENGE_TIMEOUT),1200) \
	  ingest cv-tailor ingest --keywords warmup --limit 0

.PHONY: docker-vnc
docker-vnc: ## Print VNC connect info (attach a viewer to solve OTP/CAPTCHA)
	@echo "Run an ingest/login target first (the port only exists while it runs)."
	@echo "Local : attach viewer to 127.0.0.1:5900 (default bind)."
	@echo "Tailnet: VNC_BIND=<tailnet-ip> VNC_PASSWORD=<pw> make docker-login → connect to <tailnet-ip>:5900"

.PHONY: docker-shell
docker-shell: ## Open a shell in the ingest container
	docker compose run --rm ingest bash

.PHONY: docker-generate
docker-generate: ## Generate a tailored application in-container from a captured JD → vault/applications/: make docker-generate SLUG=<slug>
	@test -n "$(SLUG)" || { echo "SLUG required, e.g. make docker-generate SLUG=acme-platform-engineer-123"; exit 2; }
	docker compose run --rm --no-deps \
	  -e CV_TAILOR_JOBS_DIR=/app/vault/applications \
	  ingest cv-tailor new "/app/vault/jds/$(SLUG).txt" --slug "$(SLUG)"
	@echo "Generated Markdown (+ German). Render PDFs + upload on the host: make pdf SLUG=$(SLUG); make upload SLUG=$(SLUG)"

# ---- Generate (cv-tailor CLI) ----------------------------------------------

.PHONY: tailor
tailor: ## Run any raw cv-tailor CLI command: make tailor CMD="<args>"
	@test -n "$(CMD)" || { echo 'CMD is required, e.g. make tailor CMD="gmail search --query unread"'; exit 2; }
	$(UV_RUN) cv-tailor $(CMD)

.PHONY: new
new: ## Generate a tailored application: make new SOURCE=job.txt [SLUG= RECIPIENT= PROVIDER= MODEL= OLLAMA_URL=]
	@test -n "$(SOURCE)" || { echo "SOURCE is required, e.g. make new SOURCE=path/to/job.txt"; exit 2; }
	$(UV_RUN) cv-tailor new "$(SOURCE)" \
	  $(if $(SLUG),--slug "$(SLUG)") \
	  $(if $(RECIPIENT),--recipient "$(RECIPIENT)") \
	  $(if $(PROVIDER),--provider "$(PROVIDER)") \
	  $(if $(MODEL),--model "$(MODEL)") \
	  $(if $(OLLAMA_URL),--ollama-url "$(OLLAMA_URL)")

.PHONY: translate
translate: ## Generate German cv.de.md / cover-letter.de.md: make translate ID=<id-or-slug>
	@test -n "$(ID)" || { echo "ID required (numeric job id or full slug)"; exit 2; }
	$(UV_RUN) cv-tailor translate "$(ID)" $(if $(PROVIDER),--provider "$(PROVIDER)") $(if $(MODEL),--model "$(MODEL)") $(if $(OLLAMA_URL),--ollama-url "$(OLLAMA_URL)")

.PHONY: pdf
pdf: ## Render the LaTeX CV + cover letter and compile to PDFs: make pdf ID=<id-or-slug>
	@test -n "$(ID)" || { echo "ID required (numeric job id or full slug)"; exit 2; }
	$(UV_RUN) cv-tailor pdf "$(ID)"

.PHONY: upload
upload: ## Compile + upload PDFs to Google Drive (needs .env): make upload ID=<id-or-slug>
	@test -n "$(ID)" || { echo "ID required (numeric job id or full slug)"; exit 2; }
	$(UV_RUN) cv-tailor upload "$(ID)"

.PHONY: db-push
db-push: ## Push filesystem application markdown files to the database: make db-push [ID=<slug>]
	$(UV_RUN) cv-tailor db push $(ID)

.PHONY: db-pull
db-pull: ## Pull database application markdown files to the filesystem: make db-pull [ID=<slug>]
	$(UV_RUN) cv-tailor db pull $(ID)

.PHONY: db-export
db-export: ## Export the entire database state to application-data/ on disk
	$(UV_RUN) cv-tailor db export

.PHONY: sheet-push
sheet-push: ## Push PostgreSQL application statuses and metadata to Google Sheets
	$(UV_RUN) cv-tailor status push

.PHONY: sheet-pull
sheet-pull: ## Pull Google Sheets status changes and metadata back to PostgreSQL
	$(UV_RUN) cv-tailor status pull

.PHONY: status
status: ## Advance an application's lifecycle: make status ID=<id-or-slug> STATUS=applied
	@test -n "$(ID)" -a -n "$(STATUS)" || { echo "Usage: make status ID=<job-id> STATUS=draft|applied|interview|offer|rejected|withdrawn"; exit 2; }
	$(UV_RUN) cv-tailor status "$(ID)" "$(STATUS)"

.PHONY: archive
archive: ## Move Drive folder to Archive/, set status withdrawn: make archive ID=<id-or-slug>
	@test -n "$(ID)" || { echo "ID required (numeric job id or full slug)"; exit 2; }
	$(UV_RUN) cv-tailor archive "$(ID)"

# ---- Build & serve ---------------------------------------------------------

.PHONY: build
build: ## Build the public MkDocs portfolio into ./site (no gate)
	$(UV_RUN) mkdocs build --clean

docs: build ## Alias for build

.PHONY: serve
serve: ## Live-preview the portfolio (mkdocs serve) on localhost (PORT=8000)
	$(UV_RUN) mkdocs serve -a localhost:$(PORT)

.PHONY: public-pdf
public-pdf: ## Compile the public 1-page CV PDF (latex/resume.tex → doc-pages/assets/cv.pdf)
	cd latex && $(MAKE) docker && cp resume.pdf ../doc-pages/assets/cv.pdf && echo "wrote doc-pages/assets/cv.pdf"

# ---- Test & quality --------------------------------------------------------

.PHONY: test
test: ## Run the unit tests (ranking + render logic; no browser, no API key)
	$(UV_RUN) pytest -q

.PHONY: check
check: test build ## Pre-push sanity: run tests, then build the portfolio

# ---- Housekeeping ----------------------------------------------------------

.PHONY: clean
clean: ## Remove build artifacts (site/, build/, caches, *.egg-info)
	rm -rf site build .pytest_cache *.egg-info
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	@echo "cleaned."
