#!/usr/bin/env python3
from config import DCA_USD_AMOUNT, DCA_FREQUENCY
from config import AUTO_WITHDRAWL, WITHDRAW_EVERY_X_BUY, MASTER_PUBLIC_KEY, BEGINNING_ADDRESS
from config import GMAIL_USER_NAME, EMAIL_NOTICE_RECEIVER

from coinbase_pro import CoinbasePro
from address_selector import AddressSelector
from email_notification import EmailNotification
from logger import Logger

import os
import time
import datetime

API_KEY = os.environ['API_KEY']
API_SECRET = os.environ['API_SECRET']
PASSPHRASE = os.environ['PASSPHRASE']
GMAIL_PASSWORD = os.environ['GMAIL_PASSWORD']
address_selector = AddressSelector(MASTER_PUBLIC_KEY, BEGINNING_ADDRESS)
logger = Logger()
next_buy_datetime = datetime.datetime.now() + datetime.timedelta(0, DCA_FREQUENCY)

if GMAIL_USER_NAME is not None:
  email_notification = EmailNotification(GMAIL_USER_NAME, GMAIL_PASSWORD, EMAIL_NOTICE_RECEIVER)

while True:
  logger.info('--------------------------------------------------')
  logger.info(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

  coinbase_pro = CoinbasePro(API_KEY, API_SECRET, PASSPHRASE)
  # Buy Bitcoin
  try:
    coinbase_pro.showBalance()
    coinbase_pro.buyBitcoin(DCA_USD_AMOUNT)
  except Exception as e:
    logger.error(f"Error: {str(e)}")
    logger.error("Waiting for 60 seconds to retry ...")
    logger.error()
    time.sleep(60)
    continue
  
  # Show the new balance and withdraw BTC if needed
  try:
    coinbase_pro.showBalance()

    if AUTO_WITHDRAWL and coinbase_pro.getUnwithdrawnBuysCount() >= WITHDRAW_EVERY_X_BUY:
      if email_notification is not None:
        email_notification.sendEmailNotification(coinbase_pro.db_manager.getUnwithdrawnBuyOrders())
      coinbase_pro.withdrawBitcoin(coinbase_pro.getBitcoinBalance(), address_selector.getWithdrawAddress())
      address_selector.incrementAddressIndex()
  except Exception as e:
    logger.error(f"Error: {str(e)}")

  # Wait for next buy time
  logger.info(f"Waiting until {next_buy_datetime.strftime('%Y-%m-%d %H:%M:%S')} to buy ${DCA_USD_AMOUNT} Bitcoin...")
  logger.info()
  while datetime.datetime.now() < next_buy_datetime:
    time.sleep(1)
  next_buy_datetime = next_buy_datetime + datetime.timedelta(0, DCA_FREQUENCY)
