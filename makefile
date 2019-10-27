PYTHON ?= python3

MYPY := $(PYTHON) -m mypy

SRC_DIR := src
DOCS_DIR := docs
HTML_BUILD := $(DOCS_DIR)/_build/html

CURRENT_BRANCH := $(shell git branch | grep \* | cut -d ' ' -f2)



.PHONY: run doc doc_server docs clean

run: $(SRC_DIR)
	@$(PYTHON) -m $<

docs:
	@make -C $(DOCS_DIR) html

doc_server: docs
	@http-server $(HTML_BUILD)

check: $(SRC_DIR)
	@$(MYPY) $<

publish_docs: docs
	@cp -r $(HTML_BUILD) html
	@touch html/.nojekill
	@git checkout gh-pages
	@find -maxdepth 1 \( ! -name ".*" ! -name 'html' ! -name 'LICENSE' \) -exec rm -rf "{}" \;
	@mv html/* .
	@mv html/.* .
	@rmdir html
	@git add .
	@git commit
	@git push origin gh-pages
	@git checkout $(CURRENT_BRANCH)

clean:
	@make -C $(DOCS_DIR) clean
