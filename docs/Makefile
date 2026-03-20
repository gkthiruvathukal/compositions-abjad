SPHINXBUILD   ?= ../.venv/bin/sphinx-build
SOURCEDIR     = .
BUILDDIR      = _build

.PHONY: help clean html latexpdf

help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)"

clean:
	rm -rf "$(BUILDDIR)"

html:
	$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)"

latexpdf:
	$(SPHINXBUILD) -M latexpdf "$(SOURCEDIR)" "$(BUILDDIR)"
