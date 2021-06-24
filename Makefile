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
clean: clean-build clean-pyc clean-test  ## remove all build, test, coverage and Python artifacts

clean-build:  ## remove build artifacts
	@rm -fr build/
	@rm -fr dist/
	@rm -fr .eggs/
	@find . -name '*.egg-info' -exec rm -fr {} +
	@find . -name '*.egg' -exec rm -f {} +

clean-pyc:  ## remove Python file artifacts
	@find . -name '*.pyc' -exec rm -f {} +
	@find . -name '*.pyo' -exec rm -f {} +
	@find . -name '*~' -exec rm -f {} +
	@find . -name '__pycache__' -exec rm -fr {} +

clean-test:  ## remove test and coverage artifacts
	@rm -fr .tox/
	@rm -f .coverage
	@rm -fr htmlcov/
	@rm -fr .pytest_cache

install-wheel:  ## Install wheel
	@echo "Installing wheel..."
	@pip install wheel

install: clean requirements.txt install-wheel  ## Install project dependencies.
	@echo "Installing project in dependencies..."
	@$(PYTHON_PIP) install -r requirements.txt

install-lint: clean setup.py install-wheel  ## Install lint extra dependencies.
	@echo "Installing lint extra requirements..."
	@$(PYTHON_PIP) install -e .'[lint]'

install-test: clean setup.py install-wheel ## Install test extra dependencies.
	@echo "Installing test extra requirements..."
	@$(PYTHON_PIP) install -e .'[test]'

install-deploy: clean setup.py install-wheel ## Install deploy extra dependencies.
	@echo "Installing deploy extra requirements..."
	@$(PYTHON_PIP) install -e .'[deploy]'

install-dev: clean setup.py install-wheel  ## Install development extra dependencies.
	@echo "Installing development requirements..."
	@$(PYTHON_PIP) install -e .'[development]' -r requirements.txt

update-requirements:  ## Updates the requirement.txt adding missing package dependencies
	@echo "Syncing the package requirements.txt..."
	@$(PIP_COMPILE)

# --------------------------------------------------------
# ------- Django manage.py commands ---------------------
# --------------------------------------------------------
migrations:
	@$(MANAGE_PY) makemigrations

migrate:
	@$(MANAGE_PY) migrate

run: migrate
	@echo "Starting server..."
	@$(MANAGE_PY) runserver

default-user: migrate
	@echo "Creating a default user..."
	@$(MANAGE_PY) create_default_user
	@echo "Username: admin@admin.com"
	@echo "Password: admin"

makemessages: clean-build  ## Runs over the entire source tree of the current directory and pulls out all strings marked for translation.
	@$(MANAGE_PY) makemessages --locale=en_US  --ignore=sample,django_clone
	@$(MANAGE_PY) makemessages --locale=fr  --ignore=sample,django_clone

compilemessages: makemessages ## Compiles .po files created by makemessages to .mo files for use with the built-in gettext support.
	@$(MANAGE_PY) compilemessages --ignore=.tox,sample,django_clone

test:
	@echo "Running `$(PYTHON_VERSION)` test..."
	@$(MANAGE_PY) test

# ----------------------------------------------------------
# ---------- Release the project to PyPI -------------------
# ----------------------------------------------------------
increase-version: guard-PART  ## Increase project version
	@bump2version $(PART)
	@git switch -c main

dist: clean install-deploy compilemessages  ## builds source and wheel package
	@pip install twine==3.4.1
	@python setup.py sdist bdist_wheel

release: dist  ## package and upload a release
	@twine upload dist/*

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
	@rm -f ".coverage.*" .coverage coverage.xml


# -----------------------------------------------------------
# --------- Fix lint errors ---------------------------------
# -----------------------------------------------------------
lint-fix:  ## Run black with inplace for model_clone and sample/models.py.
	@pip install black autopep8
	@black model_clone sample/models.py sample_driver sample_assignment sample_company --line-length=95
	@autopep8 -ir model_clone sample/models.py sample_driver sample_assignment sample_company --max-line-length=95

# -----------------------------------------------------------
# --------- Docs ---------------------------------------
# -----------------------------------------------------------
serve-docs:
	@npm i -g docsify-cli
	@npx docsify serve ./docs
