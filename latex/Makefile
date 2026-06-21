# Build the PDF résumé (pdfLaTeX).
#   make            -> resume.pdf (local TeX Live)
#   make docker     -> build inside the texlive/texlive container (no local TeX)
#   make clean      -> remove build artefacts

MAIN = resume

.PHONY: all docker clean
all: $(MAIN).pdf

$(MAIN).pdf: $(MAIN).tex
	latexmk -pdf -interaction=nonstopmode -halt-on-error $(MAIN).tex

docker:
	docker run --rm -v "$(CURDIR)":/work -w /work texlive/texlive:latest \
		latexmk -pdf -interaction=nonstopmode -halt-on-error $(MAIN).tex

clean:
	latexmk -C $(MAIN).tex 2>/dev/null || true
	rm -f *.aux *.log *.out *.fls *.fdb_latexmk
