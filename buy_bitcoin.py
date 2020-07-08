#!/usr/bin/env python3
from config import DCA_USD_AMOUNT, DCA_FREQUENCY, AUTO_WITHDRAWL, WITHDRAW_THRESHOLD, BTC_ADDRESSES
from coinbase_pro import CoinbasePro
from address_selector import AddressSelector

import os
import time
import datetime

API_KEY = os.environ['API_KEY']
API_SECRET = os.environ['API_SECRET']
PASSPHRASE = os.environ['PASSPHRASE']
address_selector = AddressSelector(BTC_ADDRESSES)

while True:
  coinbase_pro = CoinbasePro(API_KEY, API_SECRET, PASSPHRASE)
  try:
    coinbase_pro.refreshBalance()
  except Exception as e:
    print(f"Refresh balance failed, error: {str(e)}")
    print("Waiting for 60 seconds to retry ...")
    time.sleep(60)
    continue
  
  coinbase_pro.showBalance()
  coinbase_pro.depositUSDCFromCoinbase(DCA_USD_AMOUNT)
  coinbase_pro.convertUSDCToUSD(DCA_USD_AMOUNT)
  coinbase_pro.buyBitcoin(DCA_USD_AMOUNT)
  coinbase_pro.showBalance()

  if AUTO_WITHDRAWL and coinbase_pro.getBitcoinWorth() >= WITHDRAW_THRESHOLD and address_selector.getWithdrawAddress() :
    coinbase_pro.withdrawBitcoin(coinbase_pro.getBitcoinBalance(), address_selector.getWithdrawAddress())
    address_selector.incrementIndex()

  next_buy_datetime = datetime.datetime.now() + datetime.timedelta(0, DCA_FREQUENCY)
  print(f"Waiting until {next_buy_datetime} to buy ${DCA_USD_AMOUNT} Bitcoin...")
  time.sleep(DCA_FREQUENCY)
