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

PYTHONPATH="./coinbasepro_python" nohup python3 -u ./buy_bitcoin.py >> btc_dca.log &
echo "Bitcoin DCA started, check 'btc_dca.log' for log data."
