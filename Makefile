.PHONY: test test-fast test-cov

test:
	python -m pytest tests/ -v

test-fast:
	python -m pytest tests/ -v --ignore=tests/test_integration.py

test-cov:
	python -m pytest tests/ --cov=skills/document-everything/scripts \
		--cov-report=term-missing -v
