#!/bin/bash

echo "Your Coinbase Pro API key:"
read -s API_KEY
export API_KEY

echo "Your Coinbase Pro API secret:"
read -s API_SECRET
export API_SECRET

echo "Your Coinbase Pro API passphrase:"
read -s PASSPHRASE
export PASSPHRASE

echo "Gmail user password:"
read -s GMAIL_PASSWORD
export GMAIL_PASSWORD

export PYCOIN_CACHE_DIR=~/.pycoin_cache
export PYCOIN_BTC_PROVIDERS="blockchain.info blockexplorer.com chain.so"
export PYTHONPATH="./coinbasepro_python:./pycoin"

source venv/bin/activate
nohup python3 -u ./buy_bitcoin.py >> btc_dca.log &
echo "Bitcoin DCA started, check 'btc_dca.log' for log data."
