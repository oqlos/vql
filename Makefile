# Makefile for vql — Visual Query Language monorepo
# Core: src/vql/ | Control layer: packages/*2vql/

PYTHON ?= .venv/bin/python
PIP    ?= .venv/bin/pip
PORT   ?= 8216

PACKAGES := uri2vql nlp2vql img2vql img2svg uri2img2svg dsl2img2svg dsl2vql cli2vql rest2vql mcp2vql
PYTEST   := $(PYTHON) -m pytest tests/ packages/dsl2vql/tests -q --tb=short

.PHONY: help venv install install-dev proto test test-cov test-all \
        validate-schema serve compile clean build publish publish-confirm version goal

help:
	@echo "VQL Development Commands"
	@echo "========================"
	@echo ""
	@echo "Setup:"
	@echo "  venv             Create .venv (if missing)"
	@echo "  install          Install core vql (editable)"
	@echo "  install-dev      Install full *2vql dev stack"
	@echo ""
	@echo "Development:"
	@echo "  test             Run core + dsl2vql tests"
	@echo "  test-cov         Run tests with coverage"
	@echo "  test-all         Run all package tests"
	@echo "  proto            Regenerate dsl2vql protobuf"
	@echo "  validate-schema  Check dsl2vql JSON Schema registry"
	@echo "  compile          Smoke: COMPILE NL → VQLProgram"
	@echo "  serve            Start rest2vql on port $(PORT)"
	@echo "  clean            Remove build artifacts and caches"
	@echo ""
	@echo "Release:"
	@echo "  build            Build wheel/sdist"
	@echo "  publish          Build + twine check (dry-run)"
	@echo "  publish-confirm  Upload to PyPI"
	@echo "  version          Show VERSION file + installed package"
	@echo "  goal             Run goal -a (test + commit + publish workflow)"
	@echo ""

venv:
	@test -d .venv || python3 -m venv .venv
	@echo "venv ready: .venv/"

install: venv
	$(PIP) install -e .

install-dev: venv
	$(PIP) install -e .
	$(PIP) install -e packages/uri2vql
	$(PIP) install -e packages/nlp2vql
	$(PIP) install -e packages/dsl2vql
	$(PIP) install -e packages/cli2vql
	$(PIP) install -e packages/rest2vql
	-$(PIP) install -e packages/mcp2vql
	$(PIP) install -e ".[dev,png]" jsonschema protobuf fastapi uvicorn httpx
	@echo "dev stack installed"

proto: venv
	$(PIP) install -q grpcio-tools
	bash packages/dsl2vql/scripts/generate-proto.sh

test: venv install-dev
	@echo "Running tests..."
	$(PYTEST)

test-cov: venv install-dev
	$(PYTHON) -m pytest tests/ packages/dsl2vql/tests -v \
		--cov=vql --cov=dsl2vql --cov-report=term-missing

test-all: venv install-dev
	$(PYTHON) -m pytest tests/ packages/ -q --tb=short

validate-schema: venv install-dev
	dsl2vql validate-schema

compile: venv install-dev
	dsl2vql -c 'COMPILE "narysuj czerwone koło"' --json

serve: venv install-dev
	rest2vql serve --port $(PORT) --host 127.0.0.1

clean:
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name '*.egg-info' -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .coverage htmlcov/ .pytest_cache .goal_test_report.xml
	@echo "clean done"

build: venv
	$(PIP) install -q build
	rm -rf dist/ build/
	$(PYTHON) -m build

publish: build
	$(PIP) install -q twine
	$(PYTHON) -m twine check dist/*

publish-confirm: publish
	$(PYTHON) -m twine upload dist/*

version:
	@echo -n "VERSION file: "
	@cat VERSION
	@$(PYTHON) -c "from importlib.metadata import version; print('installed:', version('vql'))" 2>/dev/null || echo "installed: (not installed)"

goal:
	goal -a
