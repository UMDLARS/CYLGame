# Mostly taken from https://github.com/TezRomacH/python-package-template
#* Variables
SHELL := /usr/bin/env bash
PYTHON := python

#* Poetry
.PHONY: poetry-download
poetry-download:
	curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | $(PYTHON) -

.PHONY: poetry-remove
poetry-remove:
	curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | $(PYTHON) - --uninstall

#* Formatters
.PHONY: codestyle
codestyle:
	poetry run isort --settings-path pyproject.toml ./
	poetry run black --config pyproject.toml ./

.PHONY: format
format: codestyle

#* Linting
.PHONY: test
test:
	poetry run pytest -c pyproject.toml

.PHONY: check-codestyle
check-codestyle:
	poetry run isort --diff --check-only --settings-path pyproject.toml ./
	poetry run black --diff --check --config pyproject.toml ./

.PHONY: mypy
mypy:
	poetry run mypy --config-file pyproject.toml CYLGame

.PHONY: lint
lint: test check-codestyle mypy

.PHONY: build
build:
	poetry build

.PHONY: publish
publish: build
	poetry publish

.PHONY: build-docs
build-docs:
	poetry run bash -c "cd docs; make html"