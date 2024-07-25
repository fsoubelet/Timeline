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

.PHONY : help clean format install lint

all: install

help:
	@echo "Please use 'make $(R)<target>$(E)' where $(R)<target>$(E) is one of:"
	@echo "  $(R) build $(E)  \t  to build wheel and source distribution with $(P)Hatch$(E)."
	@echo "  $(R) clean $(E)  \t  to recursively remove build, run and bitecode files/dirs."
	@echo "  $(R) format $(E)  \t  to check and format code with $(P)Ruff$(E) through $(P)Hatch$(E)."
	@echo "  $(R) install $(E)  \t  to $(C)pip install$(E) this package into the current environment."
	@echo "  $(R) lint $(E)  \t  to lint-check the code with $(P)Ruff$(E)."

build:
	@echo "Re-building wheel and dist"
	@rm -rf dist
	@hatch build --clean
	@echo "Created build is located in the $(C)dist$(E) folder."

clean:
	@echo "Cleaning up distutils remains."
	@rm -rf build
	@rm -rf dist
	@rm -rf pytimeline.egg-info
	@rm -rf .eggs
	@echo "Cleaning up bitecode files and python cache."
	@find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete
	@echo "Cleaning up Jupyter notebooks cache."
	@find . -type d -name "*.ipynb_checkpoints" -exec rm -rf {} +
	@echo "All cleaned up!\n"

format:
	@echo "Checking code with Ruff through Hatch."
	@hatch fmt

install: format clean
	@echo "Installing (editable) with $(D)pip$(E) in the current environment."
	@python -m pip install --editable . -v

lint: format
	@echo "Checking code with Ruff through Hatch."
	@hatch fmt

# Catch-all unknow targets without returning an error. This is a POSIX-compliant syntax.
.DEFAULT:
	@echo "Make caught an invalid target."
	@echo "See help output below for available targets."
	@echo ""
	@make help
