PYTHON ?= python3
UV ?= uv
UV_CACHE_DIR ?= $(PWD)/.uv-cache
VENV ?= .venv
ACTIVATE = source $(VENV)/bin/activate
PYTHONPATH := src

.PHONY: install lint format test coverage run openapi docker-build docker-up docker-down clean

install:
	UV_CACHE_DIR=$(UV_CACHE_DIR) $(UV) venv --python $(PYTHON) $(VENV)
	UV_CACHE_DIR=$(UV_CACHE_DIR) $(UV) pip install --python $(VENV)/bin/python -e .[dev]

lint:
	$(ACTIVATE) && black --check src tests

format:
	$(ACTIVATE) && ruff check --fix src tests

test:
	$(ACTIVATE) && PYTHONPATH=$(PYTHONPATH) pytest --cov=src/svc_catalogue --cov-report=term-missing  --cov-report=xml

coverage:
	$(ACTIVATE) && coverage html

run:
	$(ACTIVATE) && AUTH_TOKEN=change-me PYTHONPATH=$(PYTHONPATH) uvicorn svc_catalogue.main:app --reload --host 0.0.0.0 --port 8000

openapi:
	$(ACTIVATE) && PYTHONPATH=$(PYTHONPATH) python -m svc_catalogue.scripts.export_openapi --output openapi.json

clean:
	rm -rf $(VENV) .pytest_cache htmlcov .coverage

docker-build:
	docker build -t svc-catalogue:local .

docker-up:
	docker-compose up --build

docker-down:
	docker-compose down -v
