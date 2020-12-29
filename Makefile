.PHONY: init setup start_dca stop_dca lint

init:
	./scripts/init.sh
	cp config_template.ini config.ini

update_secrets:
	. venv/bin/activate && ./bitcoin_dca/setup.py

setup: init update_secret

start_dca:
	./scripts/stop_dca.sh && ./scripts/start_dca.sh

stop_dca:
	./scripts/stop_dca.sh

lint:
	. venv/bin/activate && pylint bitcoin_dca/*.py
