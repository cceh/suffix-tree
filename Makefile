.PHONY: lint test dist upload docs

ENV=.venv
BIN=$(ENV)/bin/
DIRS=src/ tests/ scripts/ docs/
BROWSER=firefox
PYTEST=pytest --doctest-modules --doctest-glob="*.rst" --doctest-ignore-import-errors

all: lint test

black:
	-$(BIN)black $(DIRS)

blackdoc:
	-$(BIN)blackdoc $(DIRS)

pylint:
	-$(BIN)pylint src/

mypy:
	-$(BIN)mypy $(DIRS)

doc8:
	-$(BIN)doc8 README.rst

pydocstyle:
	-$(BIN)pydocstyle src/

lint: black blackdoc pylint mypy pydocstyle

test:
	$(BIN)python -m $(PYTEST) src/ tests/ docs/ README.rst

test-performance:
	$(BIN)python -m $(PYTEST) --performance tests/performance/

coverage:
	$(BIN)coverage erase
	$(BIN)coverage run --branch --source=src -m $(PYTEST) tests/
	$(BIN)coverage run --append --branch --source=src -m $(PYTEST) --debug-mode tests/
	$(BIN)coverage html
	$(BROWSER) htmlcov/index.html
	$(BIN)coverage json -o - | $(BIN)python tests/make_coverage_badge.py > docs/_images/badge-coverage.svg

profile:
	$(BIN)python -O -m scripts.profile

docs:
	cd docs; make SPHINXBUILD='../$(BIN)python -msphinx' html

tox:
	$(BIN)tox

dist: clean tox coverage docs
	$(BIN)python -m build
	$(BIN)twine check dist/*

upload: dist
	$(BIN)twine check dist/*
	$(BIN)twine upload dist/*

install:
	python -m venv --clear $(ENV)
	$(BIN)pip install -r requirements-dev.txt
	$(BIN)pip install --force-reinstall -e .

uninstall:
	$(BIN)pip uninstall suffix_tree

clean:
	-rm -rf build dist docs/_build htmlcov .mypy_cache .pytest_cache .tox *.egg-info
	-rm docs/_images/badge*.svg
	-rm *~ .*~ pylintgraph.dot
	-find . -name __pycache__ -type d -exec rm -r "{}" \;
