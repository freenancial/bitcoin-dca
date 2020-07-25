import itertools
import math
import time

import _path_init  # pylint: disable=unused-import
from coinbasepro_python import cbpro

import db_manager
from logger import Logger


class CoinbasePro:
    def __init__(self, api_key, api_secret, passphrase):
        self.auth_client = cbpro.AuthenticatedClient(
            api_key, api_secret, passphrase)
        self.db_manager = db_manager.DBManager()

    def refresh(self):
        self.accounts = self.auth_client.get_accounts()
        self.coinbase_accounts = self.auth_client.get_coinbase_accounts()

        self.usdc_account = self.getAccount('USDC')
        self.usd_account = self.getAccount('USD')
        self.btc_account = self.getAccount('BTC')
        self.coinbase_usdc_account = self.getCoinbaseAccount('USDC')
        time.sleep(1)

    def getAccount(self, currency):
        try:
            return next(account for account in self.accounts if account['currency'] == currency)
        except Exception as e:
            Logger.error(
                f"Failed to get account info of currency {currency} from accounts:")
            Logger.error(self.accounts)
            raise e

    def getCoinbaseAccount(self, currency):
        try:
            return next(account for account in self.coinbase_accounts if account['currency'] == currency)
        except Exception as e:
            Logger.error(
                f"Failed to get account info of currency {currency} from coinbase_accounts:")
            Logger.error(self.coinbase_accounts)
            raise e

    def showBalance(self):
        self.refresh()
        Logger.info('')
        Logger.info("Coinbase USDC balance: ${:.2f}".format(
            float(self.coinbase_usdc_account['balance'])))
        Logger.info("USDC balance: ${:.2f}".format(
            math.floor(self.usdc_balance() * 100) / 100))
        Logger.info("USD balance: ${:.2f}".format(
            math.floor(self.usd_balance() * 100) / 100))
        Logger.info("BTC balance: ₿{}".format(
            float(self.btc_account['balance'])))
        Logger.info('')

    def getUnwithdrawnBuysCount(self):
        return self.db_manager.getUnwithdrawnBuysCount()

    def depositUSDCFromCoinbase(self, amount):
        self.refresh()

        amount = math.ceil(amount * 100) / 100
        Logger.info(f"Depositing ${amount} USDC from Coinbase ...")
        self.auth_client.coinbase_deposit(
            amount, 'USDC', self.coinbase_usdc_account['id'])
        time.sleep(5)
        Logger.info('  Done')

    def convertUSDCToUSD(self, amount):
        self.refresh()

        amount = math.ceil(amount * 100) / 100
        if self.usdc_balance() < amount:
            self.depositUSDCFromCoinbase(amount - self.usdc_balance())

        Logger.info(f"Converting ${amount} USDC to USD ...")
        self.auth_client.convert_stablecoin(amount, 'USDC', 'USD')
        time.sleep(5)
        Logger.info('  Done')

    def buyBitcoin(self, usd_amount):
        self.refresh()

        usd_amount = math.ceil(usd_amount * 100) / 100
        if self.usd_balance() < usd_amount:
            self.convertUSDCToUSD(usd_amount - self.usd_balance())

        Logger.info(f"Buying ${usd_amount} Bitcoin ...")
        product_id = 'BTC-USD'
        order_result = self.auth_client.place_market_order(
            product_id, 'buy', funds=usd_amount)
        while not order_result['settled']:
            time.sleep(1)
            order_result = self.auth_client.get_order(order_result['id'])
        self.printOrderResult(order_result)
        self.db_manager.saveBuyTransaction(
            date=order_result['done_at'],
            cost=round(float(order_result['specified_funds']), 2),
            size=order_result['filled_size'],
        )
        time.sleep(5)

    def usdc_balance(self):
        return float(self.usdc_account['balance'])

    def usd_balance(self):
        return float(self.usd_account['balance'])

    def printOrderResult(self, order_result):
        Logger.info(
            f"  Cost: \t{ round( float(order_result['specified_funds']), 2 )}")
        Logger.info(f"  Size: \t{ order_result['filled_size'] }")
        Logger.info(
            f"  Price: \t{ round( float(order_result['funds']) / float(order_result['filled_size']), 2 ) }")
        Logger.info(f"  Fee: \t{ order_result['fill_fees'] }")
        Logger.info(f"  Date: \t{ order_result['done_at'] }")

    def withdrawBitcoin(self, amount, address):
        Logger.info(f"Withdrawing ₿{amount} Bitcoin to address {address} ...")
        withdraw_result = self.auth_client.crypto_withdraw(
            amount, 'BTC', address)
        Logger.info(withdraw_result)
        self.db_manager.updateWithdrawAddressForBuyOrders(address)
        Logger.info('')

    def getBitcoinWorth(self):
        return self.getBitcoinBalance() * self.getBitcoinPrice()

    def getBitcoinBalance(self):
        return float(self.btc_account['balance'])

    def getBitcoinPrice(self):
        return float(self.auth_client.get_product_order_book('BTC-USD', level=1)['bids'][0][0])
