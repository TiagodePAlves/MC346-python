PYTHON ?= python3

MYPY := $(PYTHON) -m mypy

SRC_DIR := src
DOCS_DIR := docs
HTML_BUILD := $(DOCS_DIR)/_build/html

CURRENT_BRANCH := $(shell git branch | grep \* | cut -d ' ' -f2)
HTML_TMP := html


.PHONY: run doc doc_server docs clean publish_docs check $(HTML_TMP)

run: $(SRC_DIR)
	@$(PYTHON) -m $<

docs:
	@make -C $(DOCS_DIR) html

doc_server: docs
	@http-server $(HTML_BUILD)

check: $(SRC_DIR)
	@$(MYPY) $<

$(HTML_TMP): docs
	cp -r $(HTML_BUILD) .
	touch $(HTML_TMP)/.nojekyll

publish_docs: $(HTML_TMP)
	@git checkout gh-pages
	@find -maxdepth 1 \( ! -name '.*' ! -name '$(HTML_TMP)' ! -name 'LICENSE' \) -exec rm -rf "{}" \;
	@mv $(shell find $(HTML_TMP) -maxdepth 1 ! -name '$(HTML_TMP)') .
	@rmdir $(HTML_TMP)
	@git add .
	# @git commit
	# @git push origin gh-pages
	# @git checkout $(CURRENT_BRANCH)

clean:
	@make -C $(DOCS_DIR) clean
