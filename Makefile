# Copyright 2019 Felix Soubelet <felix.soubelet@cern.ch>
# MIT License

# Documentation for most of what you will see here can be found at the following links:
# for the GNU make special targets: https://www.gnu.org/software/make/manual/html_node/Special-Targets.html
# for python packaging: https://docs.python.org/3/distutils/introduction.html

# ANSI escape sequences for bold, cyan, dark blue, end, pink and red.
B = \033[1m
C = \033[96m
D = \033[34m
E = \033[0m
P = \033[95m
R = \033[31m

.PHONY : help checklist clean condaenv docker format install interrogate lines lint tests type

all: install

help:
	@echo "Please use 'make $(R)<target>$(E)' where $(R)<target>$(E) is one of:"
	@echo "  $(R) clean $(E)  \t  to recursively remove build, run, and bitecode files/dirs."
	@echo "  $(R) format $(E)  \t  to recursively apply PEP8 formatting through the $(P)Black$(E) cli tool."
	@echo "  $(R) install $(E)  \t  to $(D)poetry install$(E) this package into the project's virtual environment."
	@echo "  $(R) lint $(E)  \t  to lint the code though $(P)Pylint$(E)."
	@echo "  $(R) tests $(E)  \t  to run tests with the $(P)pytest$(E) package."
	@echo "  $(R) type $(E)  \t  to run type checking with the $(P)mypy$(E) package."

build:
	@echo "Re-building wheel and dist"
	@rm -rf dist
	@poetry build
	@echo "Created build is located in the $(C)dist$(E) folder."

clean:
	@echo "Cleaning up documentation pages."
	@rm -rf doc_build
	@echo "Cleaning up distutils remains."
	@rm -rf build
	@rm -rf dist
	@rm -rf pyhdtoolkit.egg-info
	@rm -rf .eggs
	@echo "Cleaning up bitecode files and python cache."
	@find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete
	@echo "Cleaning up pytest cache & test artifacts."
	@find . -type d -name '*.pytest_cache' -exec rm -rf {} + -o -type f -name '*.pytest_cache' -exec rm -rf {} +
	@find . -type f -name 'fc.*' -delete -o -type f -name 'fort.*' -delete
	@echo "Cleaning up mypy cache."
	@find . -type d -name "*.mypy_cache" -exec rm -rf {} +
	@echo "Cleaning up coverage reports."
	@find . -type f -name '.coverage*' -exec rm -rf {} + -o -type f -name 'coverage.xml' -delete
	@echo "All cleaned up!\n"

format:
	@echo "Sorting imports and formatting code to PEP8, default line length is 110 characters."
	@poetry run isort . && black .

install: format clean
	@echo "Installing through $(D)Poetry$(E), with dev dependencies but no extras."
	@poetry install -v

lint: format
	@echo "Linting code"
	@poetry run pylint pyhdtoolkit/

tests: format clean
	@poetry run pytest --no-flaky-report # -p no:sugar
	@make clean

type: format
	@echo "Checking code typing with mypy, ignore $(C)pyhdtoolkit/scripts$(E)"
	@poetry run mypy --pretty --no-strict-optional --show-error-codes --warn-redundant-casts --ignore-missing-imports --follow-imports skip pyhdtoolkit/scripts/
	@make clean

# Catch-all unknow targets without returning an error. This is a POSIX-compliant syntax.
.DEFAULT:
	@echo "Make caught an invalid target! See help output below for available targets."
	@make help
