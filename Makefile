.PHONY: init setup start_dca stop_dca lint

init:
	./scripts/setup.sh

setup: init
	. venv/bin/activate && ./bitcoin_dca/setup.py

start_dca:
	./scripts/start_dca.sh

stop_dca:
	./scripts/stop_dca.sh

lint:
	. venv/bin/activate && pylint bitcoin_dca/*.py
