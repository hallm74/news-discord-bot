.PHONY: run dry-run test lint

run:
	PYTHONPATH=src python src/main.py

dry-run:
	PYTHONPATH=src python src/main.py --dry-run

test:
	PYTHONPATH=src pytest

lint:
	PYTHONPATH=src ruff check src tests
