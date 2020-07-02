#!/usr/bin/env python3

import os
import time
from coinbase import CoinbasePro

API_KEY = os.environ['API_KEY']
API_SECRET = os.environ['API_SECRET']
PASSPHRASE = os.environ['PASSPHRASE']
coinbase_pro = CoinbasePro(API_KEY, API_SECRET, PASSPHRASE)

while True:
  time.sleep(3600)
  coinbase_pro.depositUSDFromCoinbase(5)
  coinbase_pro.buyBitcoin(5)
