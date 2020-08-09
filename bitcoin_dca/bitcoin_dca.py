#!/usr/bin/env python3

"""The module is the entry point of bitcoin-dca.
"""
import datetime
import os
import time

import ahr999_index
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
from secret import Secret


class BitcoinDCA:
    def __init__(self, encription_pass):
        self.secrets = Secret.decryptAllSecrets(encryption_pass)
        if GMAIL_USER_NAME is not None:
            self.email_notification = EmailNotification(
                GMAIL_USER_NAME, self.secrets["gmail_password"], EMAIL_NOTICE_RECEIVER
            )
        if AUTO_WITHDRAWL:
            self.address_selector = AddressSelector(
                MASTER_PUBLIC_KEY, BEGINNING_ADDRESS
            )
        self.db_manager = DBManager()
        self.next_buy_datetime = self.calcFirstBuyTime()
        self.coinbase_pro = self.newCoinbaseProClient()

    def newCoinbaseProClient(self):
        return CoinbasePro(
            self.secrets["api_key"],
            self.secrets["api_secret"],
            self.secrets["passphrase"],
        )

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
        self.coinbase_pro.showBalance()

        while True:
            self.waitForNextBuyTime()

            Logger.info("--------------------------------------------------")

            # Skip buying bitcoin if ahr999 index is above 5.0
            try:
                ahr999_index_value = ahr999_index.getCurrentIndexValue()
                Logger.info(f"ahr999_index: {ahr999_index_value}")
                if ahr999_index_value > 5.0:
                    Logger.info("ahr999_index is over 5.0")
                    Logger.info("Skip this round of Bitcoin purchase")
                    self.next_buy_datetime += datetime.timedelta(0, DCA_FREQUENCY)
                    continue
            except Exception as error:  # pylint: disable=broad-except
                Logger.critical(f"Getting ahr999_index failed: {error}")

            # Buy Bitcoin
            self.coinbase_pro = self.newCoinbaseProClient()
            try:
                self.coinbase_pro.showBalance()
                self.coinbase_pro.buyBitcoin(DCA_USD_AMOUNT)
            except Exception as error:  # pylint: disable=broad-except
                Logger.error(f"Buy Bitcoin failed: {str(error)}")
                Logger.error("Waiting for 60 seconds to retry ...")
                time.sleep(60)
                continue

            # Show the new balance and withdraw Bitcoin if needed
            try:
                self.coinbase_pro.showBalance()
                if self.timeToWithdraw():
                    self.sendEmailNotification()
                    self.withdrawAllBitcoin()
            except Exception as error:  # pylint: disable=broad-except
                Logger.error(f"Withdraw Bitcoin failed: {str(error)}")

            self.next_buy_datetime += datetime.timedelta(0, DCA_FREQUENCY)

    def timeToWithdraw(self):
        return (
            self.address_selector is not None
            and self.coinbase_pro.getUnwithdrawnBuysCount() >= WITHDRAW_EVERY_X_BUY
        )

    def sendEmailNotification(self):
        if self.email_notification is not None:
            self.email_notification.sendEmailNotification(
                self.db_manager.getUnwithdrawnBuyOrders()
            )

    def withdrawAllBitcoin(self):
        self.coinbase_pro.withdrawBitcoin(
            self.coinbase_pro.btcAccount().balance,
            self.address_selector.getWithdrawAddress(),
        )
        self.address_selector.incrementAddressIndex()

    def waitForNextBuyTime(self):
        if datetime.datetime.now() > self.next_buy_datetime:
            return

        # Wait for next buy time
        Logger.info(
            f"Waiting until {self.next_buy_datetime.strftime('%Y-%m-%d %H:%M:%S')} "
            f"to buy ${DCA_USD_AMOUNT} Bitcoin..."
        )
        Logger.info("")
        while datetime.datetime.now() < self.next_buy_datetime:
            time.sleep(1)


if __name__ == "__main__":
    encryption_pass = os.environ["ENCRYPTION_PASS"]
    bitcoin_dca = BitcoinDCA(encryption_pass)
    bitcoin_dca.startDCA()
