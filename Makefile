# Self-Documented Makefile see https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html

.DEFAULT_GOAL := help

PYTHON 			:= /usr/bin/env python
PYTHON_VERSION  := $(PYTHON) --version
MANAGE_PY 		:= $(PYTHON) manage.py
PYTHON_PIP  	:= /usr/bin/env pip
PIP_COMPILE 	:= /usr/bin/env pip-compile
PART 			:= patch
PACKAGE_VERSION = $(shell $(PYTHON) setup.py --version)

# Put it first so that "make" without argument is like "make help".
help:
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-32s-\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.PHONY: help

guard-%: ## Checks that env var is set else exits with non 0 mainly used in CI;
	@if [ -z '${${*}}' ]; then echo 'Environment variable $* not set' && exit 1; fi

# --------------------------------------------------------
# ------- Python package (pip) management commands -------
# --------------------------------------------------------

clean-build: ## Clean project build artifacts.
	@echo "Removing build assets..."
	@$(PYTHON) setup.py clean
	@rm -rf build/
	@rm -rf dist/
	@rm -rf *.egg-info

test:
	@echo "Running `$(PYTHON_VERSION)` test..."
	@$(MANAGE_PY) test

install: clean-build  ## Install project dependencies.
	@echo "Installing project in dependencies..."
	@$(PYTHON_PIP) install -r requirements.txt

install-lint: clean-build  ## Install lint extra dependencies.
	@echo "Installing lint extra requirements..."
	@$(PYTHON_PIP) install -e .'[lint]'

install-test: clean-build clean-test-all ## Install test extra dependencies.
	@echo "Installing test extra requirements..."
	@$(PYTHON_PIP) install -e .'[test]'

install-dev: clean-build  ## Install development extra dependencies.
	@echo "Installing development requirements..."
	@$(PYTHON_PIP) install -e .'[development]' -r requirements.txt

update-requirements:  ## Updates the requirement.txt adding missing package dependencies
	@echo "Syncing the package requirements.txt..."
	@$(PIP_COMPILE)

tag-build:
	@git tag v$(PACKAGE_VERSION)

release-to-pypi: increase-version tag-build  ## Release project to pypi
	@$(PYTHON_PIP) install -U twine
	@$(PYTHON) setup.py sdist bdist_wheel
	@twine upload -r pypi dist/*


# ----------------------------------------------------------
# ---------- Upgrade project version (bumpversion)  --------
# ----------------------------------------------------------
increase-version: clean-build guard-PART  ## Bump the project version (using the $PART env: defaults to 'patch').
	@git checkout master
	@git push
	@echo "Increasing project '$(PART)' version..."
	@$(PYTHON_PIP) install -q -e .'[deploy]'
	@bumpversion --verbose $(PART)
	@git-changelog . > CHANGELOG.md
	@[ -z "$(git status --porcelain)" ] && echo "No changes found." || git commit -am "Updated CHANGELOG.md."
	@git push --tags
	@git push

# ----------------------------------------------------------
# --------- Run project Test -------------------------------
# ----------------------------------------------------------
tox: install-test  ## Run tox test
	@tox

clean-test-all: clean-build  ## Clean build and test assets.
	@rm -rf .tox/
	@rm -rf test-results
	@rm -rf .pytest_cache/
	@rm -f test.db
	@rm -f .coverage.* .coverage coverage.xml


# -----------------------------------------------------------
# --------- Run black ------------------------------------
# -----------------------------------------------------------
run-black:  ## Run black with inplace for model_clone and sample/models.py.
	@pip install black
	@black model_clone sample/models.py sample_driver sample_assignment sample_company --line-length=95
