"""This module defines `CoinbasePro` class.
"""
import collections
import math
import time

import _path_init  # pylint: disable=unused-import
import db_manager
from coinbasepro_python import cbpro
from logger import Logger

Account = collections.namedtuple("Account", "id balance")


class CoinbasePro:
    def __init__(self, api_key, api_secret, passphrase, config):
        self.auth_client = cbpro.AuthenticatedClient(api_key, api_secret, passphrase)
        self.db_manager = db_manager.DBManager()
        self.accounts = []
        self.coinbase_accounts = []
        self.config = config

    def refresh(self):
        while len(self.accounts) <= 1:
            self.accounts = self.auth_client.get_accounts()
        while len(self.coinbase_accounts) <= 1
            self.coinbase_accounts = self.auth_client.get_coinbase_accounts()

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

    @property
    def coinbase_usdc_account(self):
        return self.convertRawAccount(self.getCoinbaseAccount("USDC"))

    @property
    def usd_account(self):
        return self.convertRawAccount(self.getAccount("USD"))

    @property
    def usd_balance(self):
        return self.usd_account.balance

    @property
    def usdc_account(self):
        return self.convertRawAccount(self.getAccount("USDC"))

    @property
    def usdc_balance(self):
        return self.usdc_account.balance

    @property
    def btc_account(self):
        return self.convertRawAccount(self.getAccount("BTC"))

    def showBalance(self):
        self.refresh()
        Logger.info("Current Balance:")
        Logger.info("  Coinbase: ${:.2f}".format(self.coinbase_usdc_account.balance))
        Logger.info("  USDC: ${:.2f}".format(math.floor(self.usdc_balance * 100) / 100))
        Logger.info("  USD: ${:.2f}".format(math.floor(self.usd_balance * 100) / 100))
        Logger.info("  BTC: ₿{}\n".format(self.btc_account.balance))

    @property
    def unwithdrawn_buys_count(self):
        return self.db_manager.getUnwithdrawnBuysCount()

    def depositUSDCFromCoinbase(self, amount):
        self.refresh()

        amount = math.ceil(amount * 100) / 100
        Logger.info(f"Depositing ${amount} USDC from Coinbase ...")
        result = self.auth_client.coinbase_deposit(
            amount, "USDC", self.coinbase_usdc_account.id
        )
        Logger.info(f"  {result}\n")
        time.sleep(5)

    def convertUSDCToUSD(self, amount):
        self.refresh()

        amount = math.ceil(amount * 100) / 100
        if self.usdc_balance < amount + self.config.min_usdc_balance:
            self.depositUSDCFromCoinbase(
                amount + self.config.min_usdc_balance - self.usdc_balance
            )

        Logger.info(f"Converting ${amount} USDC to USD ...")
        result = self.auth_client.convert_stablecoin(amount, "USDC", "USD")
        Logger.info(f"  {result}\n")
        time.sleep(5)

    def buyBitcoin(self, usd_amount):
        self.refresh()

        usd_amount = math.ceil(usd_amount * 100) / 100
        if self.usd_balance < usd_amount:
            self.convertUSDCToUSD(usd_amount - self.usd_balance)
            self.refresh()
            if self.usd_balance < usd_amount:
                raise Exception(
                    f"Insufficient fund, has ${self.usd_balance}, needs ${usd_amount}"
                )

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
        except Exception as error:  # pylint: disable=broad-except
            Logger.error(f"Buy Bitcoin failed, error: {error}; order_result: {order_result}")
        time.sleep(5)

    def withdrawBitcoin(self, amount, address):
        Logger.info(f"Withdrawing ₿{amount} Bitcoin to address {address} ...")
        result = self.auth_client.crypto_withdraw(amount, "BTC", address)
        Logger.info(f"  {result}\n")
        self.db_manager.updateWithdrawAddressForBuyOrders(address)

    def getBitcoinWorth(self):
        return self.btc_account.balance * self.getBitcoinPrice()

    def getBitcoinPrice(self):
        return float(
            self.auth_client.get_product_order_book("BTC-USD", level=1)["bids"][0][0]
        )

    @staticmethod
    def printOrderResult(order_result):
        cost = round(float(order_result["specified_funds"]), 2)
        Logger.info(f"  Cost: \t{ cost }")
        Logger.info(f"  Size: \t{ order_result['filled_size'] }")
        price = round(
            float(order_result["funds"]) / float(order_result["filled_size"]), 2
        )
        Logger.info(f"  Price: \t{ price }")
        Logger.info(f"  Fee: \t{ order_result['fill_fees'] }")
        Logger.info(f"  Date: \t{ order_result['done_at'] }\n")

    @staticmethod
    def convertRawAccount(raw_account):
        return Account(id=raw_account["id"], balance=float(raw_account["balance"]))
