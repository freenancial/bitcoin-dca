#!/usr/bin/env python3

"""The module is the entry point of bitcoin-dca.
"""
import datetime
import os
import time

from address_selector import AddressSelector
from coinbase_pro import CoinbasePro
from config import (
    AUTO_WITHDRAWL,
    BEGINNING_ADDRESS,
    DCA_FREQUENCY,
    DCA_USD_AMOUNT,
    EMAIL_NOTICE_RECEIVER,
    GMAIL_USER_NAME,
    MASTER_PUBLIC_KEY,
    WITHDRAW_EVERY_X_BUY,
)
from db_manager import DBManager
from email_notification import EmailNotification
from logger import Logger


class BitcoinDCA:
    def __init__(self):
        self.API_KEY = os.environ["API_KEY"]
        self.API_SECRET = os.environ["API_SECRET"]
        self.PASSPHRASE = os.environ["PASSPHRASE"]

        if GMAIL_USER_NAME is not None:
            self.email_notification = EmailNotification(
                GMAIL_USER_NAME, os.environ["GMAIL_PASSWORD"], EMAIL_NOTICE_RECEIVER
            )
        if AUTO_WITHDRAWL:
            self.address_selector = AddressSelector(
                MASTER_PUBLIC_KEY, BEGINNING_ADDRESS
            )
        self.db_manager = DBManager()
        self.next_buy_datetime = self.calcFirstBuyTime()

    def calcFirstBuyTime(self):
        last_buy_order_datetime = self.db_manager.getLastBuyOrderDatetime()
        # If we have no buy recored, we execute a buy order immediately.
        if not last_buy_order_datetime:
            return datetime.datetime.now()

        last_buy_datetime = DBManager.convertOrderDatetime(last_buy_order_datetime)
        return max(
            datetime.datetime.now(),
            last_buy_datetime + datetime.timedelta(0, DCA_FREQUENCY),
        )

    def startDCA(self):
        Logger.info("--------------------------------------------------")
        Logger.info("--------------------------------------------------")
        Logger.info("Bitcoin DCA started")
        Logger.info("")

        while True:
            self.waitForNextBuyTime()

            Logger.info("--------------------------------------------------")
            coinbase_pro = CoinbasePro(self.API_KEY, self.API_SECRET, self.PASSPHRASE)

            # Buy Bitcoin
            try:
                coinbase_pro.showBalance()
                coinbase_pro.buyBitcoin(DCA_USD_AMOUNT)
            except Exception as error:  # pylint: disable=broad-except
                Logger.error(f"Buy Bitcoin failed: {str(error)}")
                Logger.error("Waiting for 60 seconds to retry ...")
                time.sleep(60)
                continue

            # Show the new balance and withdraw Bitcoin if needed
            try:
                coinbase_pro.showBalance()
                if self.timeToWithdraw(coinbase_pro):
                    self.sendEmailNotification()
                    self.withdrawAllBitcoin(coinbase_pro)
            except Exception as error:  # pylint: disable=broad-except
                Logger.error(f"Withdraw Bitcoin failed: {str(error)}")

            self.next_buy_datetime += datetime.timedelta(0, DCA_FREQUENCY)

    def timeToWithdraw(self, coinbase_pro):
        return (
            self.address_selector is not None
            and coinbase_pro.getUnwithdrawnBuysCount() >= WITHDRAW_EVERY_X_BUY
        )

    def sendEmailNotification(self):
        if self.email_notification is not None:
            self.email_notification.sendEmailNotification(
                self.db_manager.getUnwithdrawnBuyOrders()
            )

    def withdrawAllBitcoin(self, coinbase_pro):
        coinbase_pro.withdrawBitcoin(
            coinbase_pro.btcAccount().balance,
            self.address_selector.getWithdrawAddress(),
        )
        self.address_selector.incrementAddressIndex()

    def waitForNextBuyTime(self):
        # Wait for next buy time
        Logger.info(
            f"Waiting until {self.next_buy_datetime.strftime('%Y-%m-%d %H:%M:%S')} "
            f"to buy ${DCA_USD_AMOUNT} Bitcoin..."
        )
        Logger.info("")
        while datetime.datetime.now() < self.next_buy_datetime:
            time.sleep(1)


if __name__ == "__main__":
    bitcoin_dca = BitcoinDCA()
    bitcoin_dca.startDCA()
