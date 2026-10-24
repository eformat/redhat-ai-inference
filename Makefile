PORT ?= 8887
DOCS_DIR := $(shell pwd)
SITE_DIR := $(DOCS_DIR)/www

.PHONY: install build serve test clean

install:
	cd $(DOCS_DIR) && npm install

build: install
	rm -rf $(SITE_DIR)
	cd $(DOCS_DIR) && npx antora site.yml --stacktrace
	touch $(SITE_DIR)/.nojekyll

serve: build
	@echo "Serving at http://localhost:$(PORT)"
	python3 -m http.server $(PORT) --directory $(SITE_DIR)

test:
	ansible-playbook qa-automation/e2e.yml -v

clean:
	rm -rf $(SITE_DIR)
