#!/bin/bash

echo "Password for unlocking secrets:"
read -s ENCRYPTION_PASS
export ENCRYPTION_PASS

export PYCOIN_CACHE_DIR=~/.pycoin_cache
export PYCOIN_BTC_PROVIDERS="blockchain.info blockexplorer.com chain.so"

source venv/bin/activate
rm -f nohup.out
nohup ./bitcoin_dca/bitcoin_dca.py &
echo "Bitcoin DCA started, check 'log/bitcoin_dca.log' for log data."
