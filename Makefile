.PHONY: lint test dist upload

DIRS=src/ tests/unit/ tests/performance/ scripts/
BROWSER=firefox
PYTEST=pytest --doctest-modules --doctest-glob="*.rst"

all: lint test

black:
	-black $(DIRS)

blackdoc:
	-blackdoc $(DIRS)

pylint:
	-pylint src/

mypy:
	-mypy $(DIRS)

doc8:
	-doc8 README.rst

pydocstyle:
	pydocstyle src/

lint: black blackdoc pylint mypy pydocstyle

test:
	python3 -m $(PYTEST) src/ tests/ README.rst

test-performance:
	python3 -m $(PYTEST) --performance tests/performance/

coverage:
	coverage erase
	coverage run --branch --source=src -m $(PYTEST) tests/
	coverage run --append --branch --source=src -m $(PYTEST) --debug-mode tests/
	coverage report
	coverage html
	$(BROWSER) htmlcov/index.html

dist: test
	python3 -m build

upload: dist
	twine check dist/*
	twine upload dist/*

install:
	pip3 install --force-reinstall -e .

uninstall:
	pip3 uninstall -e .

clean:
	-rm -rf dist build *.egg-info
	-rm *~ .*~ pylintgraph.dot
	-find . -name __pycache__ -type d -exec rm -r "{}" \;
