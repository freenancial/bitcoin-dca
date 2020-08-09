"""This module defines `CoinbasePro` class.
"""
import collections
import math
import time

import _path_init  # pylint: disable=unused-import
import db_manager
from coinbasepro_python import cbpro
from config import MIN_USDC_BALANCE
from logger import Logger

Account = collections.namedtuple("Account", "id balance")


class CoinbasePro:
    def __init__(self, api_key, api_secret, passphrase):
        self.auth_client = cbpro.AuthenticatedClient(api_key, api_secret, passphrase)
        self.db_manager = db_manager.DBManager()
        self.accounts = []
        self.coinbase_accounts = []

    def refresh(self):
        self.accounts = self.auth_client.get_accounts()
        time.sleep(5)
        self.coinbase_accounts = self.auth_client.get_coinbase_accounts()
        time.sleep(5)

    def getAccount(self, currency):
        try:
            return next(
                account for account in self.accounts if account["currency"] == currency
            )
        except Exception as e:
            Logger.error(f"Failed to get account info for {currency} from accounts:")
            Logger.error(self.accounts)
            raise e

    def getCoinbaseAccount(self, currency):
        try:
            return next(
                account
                for account in self.coinbase_accounts
                if account["currency"] == currency
            )
        except Exception as e:
            Logger.error(
                f"Failed to get account info for {currency} from coinbase_accounts:"
            )
            Logger.error(self.coinbase_accounts)
            raise e

    def coinbaseUSDCAccount(self):
        return self.convertRawAccount(self.getCoinbaseAccount("USDC"))

    def usdAccount(self):
        return self.convertRawAccount(self.getAccount("USD"))

    def usdcAccount(self):
        return self.convertRawAccount(self.getAccount("USDC"))

    def btcAccount(self):
        return self.convertRawAccount(self.getAccount("BTC"))

    def showBalance(self):
        self.refresh()
        Logger.info("")
        Logger.info(
            "Coinbase USDC balance: ${:.2f}".format(self.coinbaseUSDCAccount().balance)
        )
        Logger.info(
            "USDC balance: ${:.2f}".format(math.floor(self.usdc_balance() * 100) / 100)
        )
        Logger.info(
            "USD balance: ${:.2f}".format(math.floor(self.usd_balance() * 100) / 100)
        )
        Logger.info("BTC balance: ₿{}".format(self.btcAccount().balance))
        Logger.info("")

    def getUnwithdrawnBuysCount(self):
        return self.db_manager.getUnwithdrawnBuysCount()

    def depositUSDCFromCoinbase(self, amount):
        self.refresh()

        amount = math.ceil(amount * 100) / 100
        Logger.info(f"Depositing ${amount} USDC from Coinbase ...")
        result = self.auth_client.coinbase_deposit(amount, "USDC", self.coinbaseUSDCAccount().id)
        Logger.info(result)
        time.sleep(5)

    def convertUSDCToUSD(self, amount):
        self.refresh()

        amount = math.ceil(amount * 100) / 100
        if self.usdc_balance() < amount + MIN_USDC_BALANCE:
            self.depositUSDCFromCoinbase(amount + MIN_USDC_BALANCE - self.usdc_balance())

        Logger.info(f"Converting ${amount} USDC to USD ...")
        result = self.auth_client.convert_stablecoin(amount, "USDC", "USD")
        Logger.info(result)
        time.sleep(5)

    def buyBitcoin(self, usd_amount):
        self.refresh()

        usd_amount = math.ceil(usd_amount * 100) / 100
        if self.usd_balance() < usd_amount:
            self.convertUSDCToUSD(usd_amount - self.usd_balance())

        Logger.info(f"Buying ${usd_amount} Bitcoin ...")
        product_id = "BTC-USD"
        order_result = self.auth_client.place_market_order(
            product_id, "buy", funds=usd_amount
        )
        try:
            while not order_result["settled"]:
                time.sleep(5)
                order_result = self.auth_client.get_order(order_result["id"])
            self.printOrderResult(order_result)
            self.db_manager.saveBuyTransaction(
                date=order_result["done_at"],
                cost=round(float(order_result["specified_funds"]), 2),
                size=order_result["filled_size"],
            )
        except Exception:  # pylint: disable=broad-except
            Logger.error(f"Unable to fetch or parse order_result: {order_result}")
        time.sleep(5)

    def usdc_balance(self):
        return self.usdcAccount().balance

    def usd_balance(self):
        return self.usdAccount().balance

    def withdrawBitcoin(self, amount, address):
        Logger.info(f"Withdrawing ₿{amount} Bitcoin to address {address} ...")
        withdraw_result = self.auth_client.crypto_withdraw(amount, "BTC", address)
        Logger.info(withdraw_result)
        self.db_manager.updateWithdrawAddressForBuyOrders(address)
        Logger.info("")

    def getBitcoinWorth(self):
        return self.btcAccount().balance * self.getBitcoinPrice()

    def getBitcoinPrice(self):
        return float(
            self.auth_client.get_product_order_book("BTC-USD", level=1)["bids"][0][0]
        )

    @staticmethod
    def printOrderResult(order_result):
        Logger.info(f"  Cost: \t{ round( float(order_result['specified_funds']), 2 )}")
        Logger.info(f"  Size: \t{ order_result['filled_size'] }")
        Logger.info(
            f"  Price: \t{ round( float(order_result['funds']) / float(order_result['filled_size']), 2 ) }"
        )
        Logger.info(f"  Fee: \t{ order_result['fill_fees'] }")
        Logger.info(f"  Date: \t{ order_result['done_at'] }")

    @staticmethod
    def convertRawAccount(raw_account):
        return Account(id=raw_account["id"], balance=float(raw_account["balance"]))
