.PHONY: init start_dca stop_dca

init:
	./setup.sh

start_dca:
	./start_dca.sh

stop_dca:
	kill $(ps aux|grep "[b]uy_bitcoin.py" |  awk '{print $2}')