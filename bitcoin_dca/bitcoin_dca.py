#!/usr/bin/env python3

"""The module is the entry point of bitcoin-dca.
"""
import datetime
import getpass
import os
import time

import ahr999_index
from address_selector import AddressSelector
from coinbase_pro import CoinbasePro
from config import Config
from db_manager import DBManager
from email_notification import EmailNotification
from logger import Logger
from secret import Secret


class BitcoinDCA:
    def __init__(self, encryption_pass=None):
        if not encryption_pass:
            encryption_pass = getpass.getpass("Encryption password: ")
        self.secrets = Secret.decryptAllSecrets(encryption_pass)
        self.config = Config("config.ini")

        if self.config.notification_gmail_user_name:
            self.email_notification = EmailNotification(
                self.config.notification_gmail_user_name,
                self.secrets["gmail_password"],
                self.config.notification_receiver,
            )
        if self.config.withdraw_every_x_buy:
            self.address_selector = AddressSelector(
                self.config.withdraw_master_public_key,
                self.config.withdraw_beginning_address,
            )
        self.db_manager = DBManager()
        self.next_buy_datetime = self.calcFirstBuyTime()
        self.coinbase_pro = self.newCoinbaseProClient()

    def newCoinbaseProClient(self):
        return CoinbasePro(
            self.secrets["api_key"],
            self.secrets["api_secret"],
            self.secrets["passphrase"],
            self.config,
        )

    def calcFirstBuyTime(self):
        last_buy_order_datetime = self.db_manager.getLastBuyOrderDatetime()
        # If we have no buy recored, we execute a buy order immediately.
        if not last_buy_order_datetime:
            return datetime.datetime.now()

        last_buy_datetime = DBManager.convertOrderDatetime(last_buy_order_datetime)
        return max(
            datetime.datetime.now(),
            last_buy_datetime + datetime.timedelta(0, self.config.dca_frequency),
        )

    def startDCA(self):
        Logger.info("----------------------")
        Logger.info("----------------------")
        Logger.info("Bitcoin DCA started\n")
        self.coinbase_pro.showBalance()

        while True:
            self.waitForNextBuyTime()

            Logger.info("----------------------")

            # Skip buying bitcoin if ahr999 index is above 5.0
            try:
                ahr999_index_value = ahr999_index.getCurrentIndexValue()
                Logger.info(f"ahr999_index: {ahr999_index_value}\n")
                if ahr999_index_value > 5.0:
                    Logger.info("ahr999_index is over 5.0")
                    Logger.info("Skip this round of Bitcoin purchase")
                    self.next_buy_datetime += datetime.timedelta(
                        0, self.config.dca_frequency
                    )
                    continue
            except Exception as error:  # pylint: disable=broad-except
                Logger.critical(f"Getting ahr999_index failed: {error}")

            # Buy Bitcoin
            self.coinbase_pro = self.newCoinbaseProClient()
            try:
                self.coinbase_pro.showBalance()
                self.coinbase_pro.buyBitcoin(self.config.dca_usd_amount)
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

            self.next_buy_datetime += datetime.timedelta(0, self.config.dca_frequency)

    def timeToWithdraw(self):
        return (
            self.address_selector is not None
            and self.coinbase_pro.unwithdrawn_buys_count
            >= self.config.withdraw_every_x_buy
        )

    def sendEmailNotification(self):
        if self.email_notification is not None:
            self.email_notification.sendEmailNotification(
                self.db_manager.getUnwithdrawnBuyOrders()
            )

    def withdrawAllBitcoin(self):
        self.coinbase_pro.withdrawBitcoin(
            self.coinbase_pro.btc_account.balance,
            self.address_selector.getWithdrawAddress(),
        )
        self.address_selector.incrementAddressIndex()

    def waitForNextBuyTime(self):
        if datetime.datetime.now() > self.next_buy_datetime:
            return

        # Wait for next buy time
        Logger.info(
            f"Waiting until {self.next_buy_datetime.strftime('%Y-%m-%d %H:%M:%S')} "
            f"to buy ${self.config.dca_usd_amount} Bitcoin...\n"
        )
        while datetime.datetime.now() < self.next_buy_datetime:
            time.sleep(1)


if __name__ == "__main__":
    bitcoin_dca = BitcoinDCA(os.environ["ENCRYPTION_PASS"])
    bitcoin_dca.startDCA()
