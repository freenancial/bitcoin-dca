.PHONY: init start_dca stop_dca lint

init:
	./scripts/setup.sh

start_dca:
	./scripts/start_dca.sh

stop_dca:
	./scripts/stop_dca.sh

lint:
	. venv/bin/activate && pylint bitcoin_dca/*.py
