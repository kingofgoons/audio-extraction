.PHONY: install dev lint format test clean

install:
	pip install .

dev:
	pip install -e ".[dev]"

lint:
	ruff check src/ tests/

format:
	ruff format src/ tests/

test:
	pytest tests/ -v

clean:
	rm -rf build dist *.egg-info .pytest_cache
