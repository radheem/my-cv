# cv-tailor — developer & application workflow.
# Run `make` (or `make help`) for the target list.
#
# Conventions:
#   * The venv is uv-managed (.venv) and has no pip — installs go through
#     `uv pip install` (see $(UVPIP)).
#   * PDFs are rendered with LaTeX (latex/*.cls) via scripts/build-application.sh
#     (local latexmk, else the texlive/texlive Docker image).
#
# Common overridable variables (make VAR=value target):
#   SOURCE   job posting URL or .txt/.md path     (required by `new`)
#   SLUG     application slug under applications/  (new/translate/pdf/upload/status)
#   RECIPIENT cover-letter salutation name         (new)
#   PROVIDER  anthropic | ollama                   (new/translate)
#   MODEL     model id override                    (new/translate)
#   OLLAMA_URL OpenAI-compatible base URL          (new/translate)
#   STATUS / SLUG  lifecycle update                (status)
#   PORT     dev server port (default 8000)

VENV    := .venv
BIN     := $(VENV)/bin
PYTHON  := $(BIN)/python
UVPIP   := VIRTUAL_ENV=$(VENV) uv pip install
PORT    ?= 8000

# mkdocs/cv-tailor run from the venv; make the venv tools resolvable.
export PATH := $(abspath $(BIN)):$(PATH)

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
	@echo "  make status SLUG=acme-senior-engineer STATUS=applied"

# ---- Setup -----------------------------------------------------------------

.PHONY: venv
venv: ## Create the uv virtualenv (.venv) if missing
	@test -d $(VENV) || uv venv $(VENV)

.PHONY: install
install: venv ## Install base deps (site build + gate; no API key)
	$(UVPIP) -e .

.PHONY: install-generate
install-generate: venv ## Install generation deps (Anthropic API + URL fetch)
	$(UVPIP) -e '.[generate,fetch]'

.PHONY: install-ollama
install-ollama: venv ## Install local Ollama / OpenAI-compatible backend
	$(UVPIP) -e '.[ollama]'

.PHONY: install-dev
install-dev: venv ## Install dev deps (pytest)
	$(UVPIP) -e '.[dev]'

.PHONY: install-all
install-all: venv ## Install everything (base + generate + fetch + ollama + dev)
	$(UVPIP) -e '.[generate,fetch,ollama,dev]'

.PHONY: playwright
playwright: ## Install the Playwright Chromium browser (needed to fetch job URLs)
	$(BIN)/playwright install chromium

# ---- LinkedIn ingest (Sprint 1) --------------------------------------------

KEYWORDS ?= platform engineer
LIMIT    ?= 5

# Run containers as the invoking host user so vault/ files match host ownership.
# (bash's $UID is readonly and not exported, so Compose can't see it — use our own vars.)
DOCKER_UID := $(shell id -u)
DOCKER_GID := $(shell id -g)
export DOCKER_UID DOCKER_GID

.PHONY: ingest
ingest: ## Run a single ad-hoc search on the HOST under Xvfb: make ingest KEYWORDS="..." [LOCATION= GEO_ID= DISTANCE= LIMIT= DAYS=7 MAX_APPLICANTS=100 EASY_APPLY=1]
	xvfb-run -a -s "-screen 0 1440x900x24" $(BIN)/cv-tailor ingest \
	  --keywords "$(KEYWORDS)" $(if $(LOCATION),--location "$(LOCATION)") --limit $(LIMIT) \
	  $(if $(GEO_ID),--geo-id "$(GEO_ID)") $(if $(DISTANCE),--distance "$(DISTANCE)") \
	  $(if $(DAYS),--days "$(DAYS)") $(if $(MAX_APPLICANTS),--max-applicants "$(MAX_APPLICANTS)") \
	  $(if $(EASY_APPLY),--easy-apply)

.PHONY: hunt
hunt: ## Run every search in config/search.yml on the HOST under Xvfb
	xvfb-run -a -s "-screen 0 1440x900x24" $(BIN)/cv-tailor hunt

.PHONY: capture
capture: ## Capture ONE job link to vault/jds/ on the HOST under Xvfb: make capture URL="https://www.linkedin.com/jobs/view/<id>"
	@test -n "$(URL)" || { echo 'URL required, e.g. make capture URL="https://www.linkedin.com/jobs/view/123"'; exit 2; }
	xvfb-run -a -s "-screen 0 1440x900x24" $(BIN)/cv-tailor capture "$(URL)"

DAYS    ?= 7
MAX_APPLICANTS ?= 100
TOP     ?= 10

.PHONY: job-hunt
job-hunt: ## Full pipeline: search 4 cities → score → generate top N → PDF → Drive → push
	bash scripts/job-hunt.sh --top $(TOP)

.PHONY: job-hunt-dry
job-hunt-dry: ## Dry run: show what job-hunt would do without running anything
	bash scripts/job-hunt.sh --top $(TOP) --dry-run

.PHONY: score
score: ## Score captured JDs and print ranking: make score [TOP=10]
	$(BIN)/python3 scripts/score-jds.py --top $(TOP)

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

.PHONY: new
new: ## Generate a tailored application: make new SOURCE=job.txt [SLUG= RECIPIENT= PROVIDER= MODEL= OLLAMA_URL=]
	@test -n "$(SOURCE)" || { echo "SOURCE is required, e.g. make new SOURCE=path/to/job.txt"; exit 2; }
	$(BIN)/cv-tailor new "$(SOURCE)" \
	  $(if $(SLUG),--slug "$(SLUG)") \
	  $(if $(RECIPIENT),--recipient "$(RECIPIENT)") \
	  $(if $(PROVIDER),--provider "$(PROVIDER)") \
	  $(if $(MODEL),--model "$(MODEL)") \
	  $(if $(OLLAMA_URL),--ollama-url "$(OLLAMA_URL)")

.PHONY: translate
translate: ## Generate German cv.de.md / cover-letter.de.md: make translate SLUG=<slug>
	@test -n "$(SLUG)" || { echo "SLUG required"; exit 2; }
	$(BIN)/cv-tailor translate "$(SLUG)" $(if $(PROVIDER),--provider "$(PROVIDER)") $(if $(MODEL),--model "$(MODEL)") $(if $(OLLAMA_URL),--ollama-url "$(OLLAMA_URL)")

.PHONY: pdf
pdf: ## Render the LaTeX CV + cover letter and compile to PDFs: make pdf SLUG=<slug>
	@test -n "$(SLUG)" || { echo "SLUG required"; exit 2; }
	$(BIN)/cv-tailor pdf "$(SLUG)"

.PHONY: upload
upload: ## Compile + upload PDFs to Google Drive (needs .env): make upload SLUG=<slug>
	@test -n "$(SLUG)" || { echo "SLUG required"; exit 2; }
	$(BIN)/cv-tailor upload "$(SLUG)"

.PHONY: track
track: ## Regenerate the applications/README.md status table
	$(BIN)/cv-tailor track

.PHONY: status
status: ## Advance an application's lifecycle: make status SLUG=<slug> STATUS=applied
	@test -n "$(SLUG)" -a -n "$(STATUS)" || { echo "Usage: make status SLUG=<slug> STATUS=draft|applied|interview|offer|rejected|withdrawn"; exit 2; }
	$(BIN)/cv-tailor status "$(SLUG)" "$(STATUS)"

# ---- Build & serve ---------------------------------------------------------

.PHONY: build
build: ## Build the public MkDocs portfolio into ./site (no gate)
	$(BIN)/mkdocs build --clean

docs: build ## Alias for build

.PHONY: serve
serve: ## Live-preview the portfolio (mkdocs serve) on localhost (PORT=8000)
	$(BIN)/mkdocs serve -a localhost:$(PORT)

.PHONY: public-pdf
public-pdf: ## Compile the public 1-page CV PDF (latex/resume.tex → docs/assets/cv.pdf)
	cd latex && $(MAKE) docker && cp resume.pdf ../docs/assets/cv.pdf && echo "wrote docs/assets/cv.pdf"

# ---- Test & quality --------------------------------------------------------

.PHONY: test
test: ## Run the unit tests (ranking + render logic; no browser, no API key)
	$(PYTHON) -m pytest -q

.PHONY: check
check: test build ## Pre-push sanity: run tests, then build the portfolio

# ---- Housekeeping ----------------------------------------------------------

.PHONY: clean
clean: ## Remove build artifacts (site/, build/, caches, *.egg-info)
	rm -rf site build .pytest_cache *.egg-info
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	@echo "cleaned."
