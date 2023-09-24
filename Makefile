.PHONY: lint test dist upload docs

ENV=env
BIN=$(ENV)/bin/
DIRS=src/ tests/unit/ tests/performance/ scripts/ docs/
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
	$(BIN)coverage report
	$(BIN)coverage html
	$(BROWSER) htmlcov/index.html

profile:
	$(BIN)python -O -m scripts.profile

docs:
	cd docs; make html

badges: test coverage
	$(BIN)python docs/make_badges.py

tox:
	$(BIN)tox

tox-e:
	$(BIN)tox -e py

dist: clean test coverage badges
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
	-rm -rf dist build *.egg-info
	-rm *~ .*~ pylintgraph.dot
	-find . -name __pycache__ -type d -exec rm -r "{}" \;
