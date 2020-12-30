#!/usr/bin/env python3

"""The module is the entry point of bitcoin-dca.
"""
import datetime
import getpass
import _thread
import os
import time

import robin_stocks
import pyotp

import ahr999_index
from address_selector import AddressSelector
from coinbase_pro import CoinbasePro
from config import default_config
from db_manager import DBManager
from email_notification import EmailNotification
from logger import Logger
from secret import Secret


class BitcoinDCA:
    def __init__(self, is_coinbase, encryption_pass=None):
        if not encryption_pass:
            encryption_pass = getpass.getpass("Encryption password: ")
        self.secrets = Secret.decryptAllSecrets(encryption_pass)

        if is_coinbase and default_config.notification_gmail_user_name:
            self.email_notification = EmailNotification(
                default_config.notification_gmail_user_name,
                self.secrets["gmail_password"],
                default_config.notification_receiver,
            )
        else:
            self.email_notification = None

        if is_coinbase and default_config.withdraw_every_x_buy:
            self.address_selector = AddressSelector(
                self.secrets["master_public_key"], self.secrets["beginning_address"],
            )
        self.db_manager = DBManager()
        self.next_robinhood_buy_datetime = self.calcRobinhoodFirstBuyTime()
        if is_coinbase:
            Logger.info("\n\n\n")
            Logger.info("----------------------")
            Logger.info("----------------------")
            Logger.info("Coinbase DCA started")
            Logger.info("")
            self.coinbase_pro = self.newCoinbaseProClient()
            self.next_buy_datetime = self.calcFirstBuyTime()

    def newCoinbaseProClient(self):
        return CoinbasePro(
            self.secrets["api_key"],
            self.secrets["api_secret"],
            self.secrets["passphrase"],
            default_config,
        )

    def calcFirstBuyTime(self):
        last_buy_order_datetime = self.db_manager.getLastBuyOrderDatetime()
        # If we have no buy recored, we execute a buy order immediately.
        if not last_buy_order_datetime:
            return datetime.datetime.now()

        last_buy_datetime = DBManager.convertOrderDatetime(last_buy_order_datetime)
        Logger.info(
            f"Last Coinbase buy order was at: {last_buy_datetime.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        Logger.info("")
        return max(
            datetime.datetime.now(),
            last_buy_datetime + datetime.timedelta(0, default_config.dca_frequency),
        )

    def calcRobinhoodFirstBuyTime(self):
        last_buy_order_datetime = self.db_manager.getRobinhoodLastBuyOrderDatetime()
        # If we have no buy recored, we execute a buy order immediately.
        if not last_buy_order_datetime:
            return datetime.datetime.now()

        last_buy_datetime = DBManager.convertOrderDatetime(last_buy_order_datetime)
        return max(
            datetime.datetime.now(),
            last_buy_datetime
            + datetime.timedelta(0, default_config.robinhood_dca_frequency),
        )

    def checkBuyingCriteria(self):
        # Skip buying bitcoin if ahr999 index is above 5.0
        try:
            ahr999_index_value = ahr999_index.getCurrentIndexValue()
            Logger.info(f"ahr999_index: {ahr999_index_value}")
            Logger.info("")
            if ahr999_index_value > 5.0:
                Logger.info("ahr999_index is over 5.0")
                Logger.info("Skip this round of Bitcoin purchase")
                self.next_buy_datetime += datetime.timedelta(
                    0, default_config.dca_frequency
                )
                return False
        except Exception as error:  # pylint: disable=broad-except
            Logger.critical(f"Getting ahr999_index failed: {error}")
        return True

    def buyBitcoinOnCoinbase(self):
        if default_config.dca_usd_amount <= 0:
            Logger.info("Skip Coinbase DCA because the dca amount is no larger than 0")
            return

        while True:
            self.coinbase_pro = self.newCoinbaseProClient()
            try:
                self.coinbase_pro.showBalance()
                self.coinbase_pro.buyBitcoin(default_config.dca_usd_amount)
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
            break

    def buyBitcoinOnRobinhood(self):
        if default_config.robinhood_dca_usd_amount <= 0:
            Logger.info("Skip Robinhood DCA because the dca amount is no larger than 0")
            return
        username = self.secrets["robinhood_user"]
        passwd = self.secrets["robinhood_password"]
        totp = self.secrets["robinhood_totp"]
        login = robin_stocks.login(username, passwd, mfa_code=pyotp.TOTP(totp).now())
        Logger.info(f"{login['detail']}\n")

        dca_amount = default_config.robinhood_dca_usd_amount
        buy_order = robin_stocks.order_buy_crypto_by_price("BTC", dca_amount)
        Logger.info(f"{buy_order}\n")

        self.db_manager.saveRobinhoodBuyTransaction(
            date=buy_order["created_at"],
            price=round(float(buy_order["price"]), 2),
            size=buy_order["quantity"],
        )

    def startCoinbaseDCA(self):
        while True:
            self.waitForNextBuyTime()

            Logger.info("----------------------")
            if not self.checkBuyingCriteria():
                self.next_buy_datetime += datetime.timedelta(
                    0, default_config.dca_frequency
                )
                continue

            self.buyBitcoinOnCoinbase()
            self.next_buy_datetime += datetime.timedelta(
                0, default_config.dca_frequency
            )

    def startRobinhoodDCA(self):
        Logger.info("----------------------")
        Logger.info("----------------------")
        Logger.info("Robinhood DCA started\n")

        while True:
            self.waitForNextRobinhoodBuyTime()

            Logger.info("----------------------")
            self.buyBitcoinOnRobinhood()
            self.next_robinhood_buy_datetime += datetime.timedelta(
                0, default_config.robinhood_dca_frequency
            )

    def timeToWithdraw(self):
        return (
            self.address_selector is not None
            and self.coinbase_pro.unwithdrawn_buys_count
            >= default_config.withdraw_every_x_buy
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
            f"to buy ${default_config.dca_usd_amount} Bitcoin on Coinbase...\n "
        )
        while datetime.datetime.now() < self.next_buy_datetime:
            time.sleep(1)

    def waitForNextRobinhoodBuyTime(self):
        if datetime.datetime.now() > self.next_robinhood_buy_datetime:
            return

        # Wait for next buy time
        Logger.info(
            f"Waiting until {self.next_robinhood_buy_datetime.strftime('%Y-%m-%d %H:%M:%S')} "
            f"to buy ${default_config.robinhood_dca_usd_amount} Bitcoin on Robinhood...\n"
        )
        while datetime.datetime.now() < self.next_robinhood_buy_datetime:
            time.sleep(1)


def robinhoodDCA():
    robinhood_dca = BitcoinDCA(False, os.environ["ENCRYPTION_PASS"])
    robinhood_dca.startRobinhoodDCA()


if __name__ == "__main__":
    if default_config.robinhood_dca_usd_amount > 0:
        _thread.start_new_thread(robinhoodDCA, ())
    time.sleep(5)
    coinbase_dca = BitcoinDCA(True, os.environ["ENCRYPTION_PASS"])
    coinbase_dca.startCoinbaseDCA()
