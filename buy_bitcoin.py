#!/usr/bin/env python3
from config import DCA_USD_AMOUNT, DCA_FREQUENCY, USE_USDC, AUTO_WITHDRAWL, WITHDRAW_THRESHOLD, BTC_ADDRESSES
from coinbase_pro import CoinbasePro

import os
import time
import datetime

API_KEY = os.environ['API_KEY']
API_SECRET = os.environ['API_SECRET']
PASSPHRASE = os.environ['PASSPHRASE']
coinbase_pro = CoinbasePro(API_KEY, API_SECRET, PASSPHRASE, use_usdc=USE_USDC)

cur_btc_address_index = 0

while True:
  coinbase_pro.refreshBalance()
  coinbase_pro.depositFromCoinbase(DCA_USD_AMOUNT)
  coinbase_pro.buyBitcoin(DCA_USD_AMOUNT)

  if AUTO_WITHDRAWL and cur_btc_address_index < len(BTC_ADDRESSES) and coinbase_pro.getBitcoinWorth() >= WITHDRAW_THRESHOLD:
    coinbase_pro.withdrawBitcoin(coinbase_pro.getBitcoinBalance(), BTC_ADDRESSES[cur_btc_address_index])
    cur_btc_address_index += 1

  next_buy_datetime = datetime.datetime.now() + datetime.timedelta(0, DCA_FREQUENCY)
  print(f"Waiting until {next_buy_datetime} to buy ${DCA_USD_AMOUNT} Bitcoin...")
  time.sleep(DCA_FREQUENCY)
