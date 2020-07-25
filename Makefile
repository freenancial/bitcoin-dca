.PHONY: init start_dca stop_dca

init:
	./scripts/setup.sh

start_dca:
	./scripts/start_dca.sh

stop_dca:
	./scripts/stop_dca.sh
