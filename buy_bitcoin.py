#!/usr/bin/env python3
from config import DCA_USD_AMOUNT, DCA_FREQUENCY

import os
import time
import datetime
from coinbase import CoinbasePro

API_KEY = os.environ['API_KEY']
API_SECRET = os.environ['API_SECRET']
PASSPHRASE = os.environ['PASSPHRASE']
coinbase_pro = CoinbasePro(API_KEY, API_SECRET, PASSPHRASE)

while True:
  next_buy_datetime = datetime.datetime.now() + datetime.timedelta(0, DCA_FREQUENCY)
  print(
      f"Waiting until {next_buy_datetime} to buy ${DCA_USD_AMOUNT} Bitcoin...")
  time.sleep(DCA_FREQUENCY)

  coinbase_pro.refreshBalance()
  coinbase_pro.depositUSDFromCoinbase(DCA_USD_AMOUNT)
  coinbase_pro.buyBitcoin(DCA_USD_AMOUNT)
