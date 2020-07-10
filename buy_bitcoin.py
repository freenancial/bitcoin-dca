#!/usr/bin/env python3
from config import DCA_USD_AMOUNT, DCA_FREQUENCY
from config import AUTO_WITHDRAWL, WITHDRAW_EVERY_X_BUY, MASTER_PUBLIC_KEY, BEGINNING_ADDRESS

from coinbase_pro import CoinbasePro
from address_selector import AddressSelector

import os
import time
import datetime

API_KEY = os.environ['API_KEY']
API_SECRET = os.environ['API_SECRET']
PASSPHRASE = os.environ['PASSPHRASE']
address_selector = AddressSelector(MASTER_PUBLIC_KEY, BEGINNING_ADDRESS)

next_buy_datetime = datetime.datetime.now() + datetime.timedelta(0, DCA_FREQUENCY)

while True:
  print('--------------------------------------------------')
  coinbase_pro = CoinbasePro(API_KEY, API_SECRET, PASSPHRASE)
  try:
    coinbase_pro.showBalance()
  except Exception as e:
    print(f"Error: {str(e)}")
    print("Waiting for 60 seconds to retry ...")
    print()
    time.sleep(60)
    continue
  
  coinbase_pro.depositUSDCFromCoinbase(DCA_USD_AMOUNT)
  coinbase_pro.convertUSDCToUSD(DCA_USD_AMOUNT)
  coinbase_pro.buyBitcoin(DCA_USD_AMOUNT)
  coinbase_pro.showBalance()

  if AUTO_WITHDRAWL and coinbase_pro.getRecentBuysCount() >= WITHDRAW_EVERY_X_BUY:
    coinbase_pro.withdrawBitcoin(coinbase_pro.getBitcoinBalance(), address_selector.getWithdrawAddress())
    address_selector.incrementAddressIndex()

  print(f"Waiting until {next_buy_datetime} to buy ${DCA_USD_AMOUNT} Bitcoin...")
  print()
  while datetime.datetime.now() < next_buy_datetime:
    time.sleep(1)
  next_buy_datetime = datetime.datetime.now() + datetime.timedelta(0, DCA_FREQUENCY)
