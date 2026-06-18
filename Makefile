# cv-tailor — developer & application workflow.
# Run `make` (or `make help`) for the target list.
#
# Conventions:
#   * The venv is uv-managed (.venv) and has no pip — installs go through
#     `uv pip install` (see $(UVPIP)).
#   * build.py shells out to `mkdocs`, so the venv bin is prepended to PATH below.
#   * GATE_PASSWORD defaults to "test" for local builds; the real value is a CI
#     secret. Override per-invocation: `make build GATE_PASSWORD=hunter2`.
#
# Common overridable variables (make VAR=value target):
#   SOURCE   job posting URL or .txt/.md path     (required by `new`)
#   SLUG     output dir name under docs/jobs/      (new)
#   RECIPIENT cover-letter salutation name         (new)
#   PROVIDER  anthropic | ollama                   (new)
#   MODEL     model id override                    (new)
#   OLLAMA_URL OpenAI-compatible base URL          (new)
#   STATUS / SLUG  lifecycle update                (status)
#   PORT     dev server port (default 8000)
#   GATE_PASSWORD  seals the gated content (default "test")

VENV    := .venv
BIN     := $(VENV)/bin
PYTHON  := $(BIN)/python
UVPIP   := VIRTUAL_ENV=$(VENV) uv pip install
PORT    ?= 8000
GATE_PASSWORD ?= test

# build.py runs `mkdocs` as a subprocess; make the venv tools resolvable.
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

.PHONY: status
status: ## Advance an application's lifecycle: make status SLUG=<slug> STATUS=applied
	@test -n "$(SLUG)" -a -n "$(STATUS)" || { echo "Usage: make status SLUG=<slug> STATUS=draft|applied|interview|offer|rejected|withdrawn"; exit 2; }
	@f=docs/jobs/$(SLUG)/index.md; \
	 test -f "$$f" || { echo "no such hub: $$f"; exit 2; }; \
	 grep -q '^status:' "$$f" || { echo "no status: field in $$f"; exit 2; }; \
	 sed -i 's/^status:.*/status: "$(STATUS)"/' "$$f"; \
	 echo "set $(SLUG) status -> $(STATUS)  (review the diff, then commit)"

# ---- Build & serve ---------------------------------------------------------

.PHONY: build
build: ## Render + AES-seal the gated site into ./site (GATE_PASSWORD=test by default)
	GATE_PASSWORD="$(GATE_PASSWORD)" $(PYTHON) build.py

.PHONY: docs
docs: ## Build the MkDocs site only (no gating) into ./site
	$(BIN)/mkdocs build --clean

.PHONY: serve
serve: ## Live-preview the docs (mkdocs serve; ungated) on localhost (PORT=8000)
	$(BIN)/mkdocs serve -a localhost:$(PORT)

.PHONY: preview
preview: build ## Build the gated site, then serve ./site to test the password gate
	@echo "Serving the GATED build at http://localhost:$(PORT) (Ctrl-C to stop)"
	$(PYTHON) -m http.server -d site $(PORT)

# ---- Test & quality --------------------------------------------------------

.PHONY: test
test: ## Run the unit tests (ranking logic; no browser, no API key)
	$(PYTHON) -m pytest -q

.PHONY: check
check: test build ## Pre-push sanity: run tests, then a full gated build

# ---- Housekeeping ----------------------------------------------------------

.PHONY: clean
clean: ## Remove build artifacts (site/, build/, caches, *.egg-info)
	rm -rf site build .pytest_cache *.egg-info
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	@echo "cleaned."
