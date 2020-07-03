from coinbasepro_python import cbpro
import time

class CoinbasePro:
  def __init__(self, api_key, api_secret, passphrase):
    self.auth_client = cbpro.AuthenticatedClient(api_key, api_secret, passphrase)

  def refreshBalance(self):
    self.accounts = self.auth_client.get_accounts()
    self.coinbase_accounts = self.auth_client.get_coinbase_accounts()

    self.usdc_account = self.getAccount('USDC')
    self.usd_account = self.getAccount('USD')
    self.btc_account = self.getAccount('BTC')
    self.coinbase_usdc_account=self.getCoinbaseAccount('USDC')

    self.showBalance()

  def getAccount(self, currency):
    return next(account for account in self.accounts if account['currency'] == currency)

  def getCoinbaseAccount(self, currency):
    return next(account for account in self.coinbase_accounts if account['currency'] == currency)

  def showBalance(self):
    print()
    print("Coinbase USDC balance: {:.2f}".format(float(self.coinbase_usdc_account['balance'])))
    print("USDC balance: {:.2f}".format(float(self.usdc_account['balance'])))
    print("USD balance: {:.2f}".format(float(self.usd_account['balance'])))
    print("BTC balance: {}".format(float(self.btc_account['balance'])))
    print()

  def depositUSDCFromCoinbase(self, amount):
    print(f"Depoisting ${amount} USDC from Coinabase ...")
    deposit_result = self.auth_client.coinbase_deposit(amount, 'USDC', self.coinbase_usdc_account['id'])
    print(deposit_result)
    self.refreshBalance()

  def convertUSDCToUSD(self, amount):
    print(f"Converting ${amount} USDC to USD ...")
    convert_result = self.auth_client.convert_stablecoin(amount, 'USDC', 'USD')
    print(convert_result)
    self.refreshBalance()

  def buyBitcoin(self, usd_amount):
    print(f"Buying ${usd_amount} Bitcoin ...")

    product_id = 'BTC-USD'
    order_result = self.auth_client.place_market_order(product_id, 'buy', funds=usd_amount)
    while not order_result['settled']:
      time.sleep(1)
      order_result = self.auth_client.get_order(order_result['id'])
    self.printOrderResult(order_result)
    self.refreshBalance()

  def printOrderResult(self, order_result):
    print(f"  Market: \t{order_result['product_id']}")
    print(f"  Size: \t{ round( float(order_result['specified_funds']), 2 )}")
    print(f"  Filled: \t{order_result['filled_size']}")
    print(f"  Filled Price: {round( float(order_result['funds']) / float(order_result['filled_size']), 2 )}")
    print(f"  Fee: \t\t{order_result['fill_fees']}")
    print(f"  Date: \t{order_result['done_at']}")

  def withdrawBitcoin(self, amount, address):
    print(f"Withdrawing ${amount} Bitcoin to address {address} ...")
    withdraw_result = self.auth_client.crypto_withdraw(amount, 'BTC', address)
    print(withdraw_result)
    print()

  def getBitcoinWorth(self):
    return self.getBitcoinBalance() * self.getBitcoinPrice()

  def getBitcoinBalance(self):
    return float(self.btc_account['balance'])

  def getBitcoinPrice(self):
    return float(self.auth_client.get_product_order_book('BTC-USD', level=1)['bids'][0][0])
