#!/usr/bin/env python3
from config import DCA_USD_AMOUNT, DCA_FREQUENCY, USE_USDC

import os
import time
import datetime
from coinbase_pro import CoinbasePro

API_KEY = os.environ['API_KEY']
API_SECRET = os.environ['API_SECRET']
PASSPHRASE = os.environ['PASSPHRASE']
coinbase_pro = CoinbasePro(API_KEY, API_SECRET, PASSPHRASE)

while True:
  coinbase_pro.refreshBalance()
  coinbase_pro.depositFromCoinbase(DCA_USD_AMOUNT, use_usdc=USE_USDC)
  coinbase_pro.buyBitcoin(DCA_USD_AMOUNT, use_usdc=USE_USDC)

  next_buy_datetime = datetime.datetime.now() + datetime.timedelta(0, DCA_FREQUENCY)
  print(f"Waiting until {next_buy_datetime} to buy ${DCA_USD_AMOUNT} Bitcoin...")
  time.sleep(DCA_FREQUENCY)
