#!/usr/bin/env python3

"""The module is the entry point of bitcoin-dca.
"""
import datetime
import os
import time

from address_selector import AddressSelector
from coinbase_pro import CoinbasePro
from config import (AUTO_WITHDRAWL, BEGINNING_ADDRESS, DCA_FREQUENCY,
                    DCA_USD_AMOUNT, EMAIL_NOTICE_RECEIVER, GMAIL_USER_NAME,
                    MASTER_PUBLIC_KEY, WITHDRAW_EVERY_X_BUY)
from email_notification import EmailNotification
from logger import Logger

API_KEY = os.environ['API_KEY']
API_SECRET = os.environ['API_SECRET']
PASSPHRASE = os.environ['PASSPHRASE']
GMAIL_PASSWORD = os.environ['GMAIL_PASSWORD']
if AUTO_WITHDRAWL:
    address_selector = AddressSelector(MASTER_PUBLIC_KEY, BEGINNING_ADDRESS)
next_buy_datetime = datetime.datetime.now() + datetime.timedelta(0, DCA_FREQUENCY)

if GMAIL_USER_NAME is not None:
    email_notification = EmailNotification(GMAIL_USER_NAME, GMAIL_PASSWORD, EMAIL_NOTICE_RECEIVER)

while True:
    Logger.info('--------------------------------------------------')
    Logger.info(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    coinbase_pro = CoinbasePro(API_KEY, API_SECRET, PASSPHRASE)
    # Buy Bitcoin
    try:
        coinbase_pro.showBalance()
        coinbase_pro.buyBitcoin(DCA_USD_AMOUNT)
    except Exception as error:  # pylint: disable=broad-except
        Logger.error('Unable to buy Bitcoin')
        Logger.error(f'Error: {str(error)}')
        Logger.error('Waiting for 60 seconds to retry ...')
        Logger.error('')
        time.sleep(60)
        continue

    # Show the new balance and withdraw BTC if needed
    try:
        coinbase_pro.showBalance()

        if AUTO_WITHDRAWL and coinbase_pro.getUnwithdrawnBuysCount() >= WITHDRAW_EVERY_X_BUY:
            if email_notification is not None:
                email_notification.sendEmailNotification(
                    coinbase_pro.db_manager.getUnwithdrawnBuyOrders())
            coinbase_pro.withdrawBitcoin(coinbase_pro.btcAccount().balance,
                                         address_selector.getWithdrawAddress())
            address_selector.incrementAddressIndex()
    except Exception as error:  # pylint: disable=broad-except
        Logger.error('Unable to withdraw Bitcoin')
        Logger.error(f"Error: {str(error)}")

    # Wait for next buy time
    Logger.info(f"Waiting until {next_buy_datetime.strftime('%Y-%m-%d %H:%M:%S')} "
                f"to buy ${DCA_USD_AMOUNT} Bitcoin...")
    Logger.info('')
    while datetime.datetime.now() < next_buy_datetime:
        time.sleep(1)
    next_buy_datetime = next_buy_datetime + datetime.timedelta(0, DCA_FREQUENCY)
