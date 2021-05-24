PYTEST_FLAGS=-vv --tb=long -l
PWD=$(shell pwd)

test:
	pytest $(PYTEST_FLAGS)

test-pdb:
	pytest $(PYTEST_FLAGS) --pdb

test-ipdb:
	pytest $(PYTEST_FLAGS) --pdb --pdbcls=IPython.terminal.debugger:TerminalPdb
