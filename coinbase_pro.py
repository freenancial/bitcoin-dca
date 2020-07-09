import cbpro
import time
import itertools

class CoinbasePro:
  def __init__(self, api_key, api_secret, passphrase):
    self.auth_client = cbpro.AuthenticatedClient(api_key, api_secret, passphrase)

  def refresh(self):
    self.accounts = self.auth_client.get_accounts()
    self.coinbase_accounts = self.auth_client.get_coinbase_accounts()

    self.usdc_account = self.getAccount('USDC')
    self.usd_account = self.getAccount('USD')
    self.btc_account = self.getAccount('BTC')
    self.coinbase_usdc_account = self.getCoinbaseAccount('USDC')

  def getAccount(self, currency):
    try:
      return next(account for account in self.accounts if account['currency'] == currency)
    except Exception as e:
      print(f"Failed to get account info of currency {currency} from accounts:")
      print(self.accounts)
      raise e

  def getCoinbaseAccount(self, currency):
    try:
      return next(account for account in self.coinbase_accounts if account['currency'] == currency)
    except Exception as e:
      print(f"Failed to get account info of currency {currency} from coinbase_accounts:")
      print(self.coinbase_accounts)
      raise e

  def showBalance(self):
    self.refresh()
    print()
    print("Coinbase USDC balance: {:.2f}".format(float(self.coinbase_usdc_account['balance'])))
    print("BTC balance: {}".format(float(self.btc_account['balance'])))
    print()

  def getRecentBuysCount(self):
    btc_account_history = self.auth_client.get_account_history(self.btc_account['id'])
    return sum(1 for _ in itertools.takewhile(lambda x: x['type'] == 'match', btc_account_history))

  def depositUSDCFromCoinbase(self, amount):
    self.auth_client.coinbase_deposit(amount, 'USDC', self.coinbase_usdc_account['id'])

  def convertUSDCToUSD(self, amount):
    self.auth_client.convert_stablecoin(amount, 'USDC', 'USD')

  def buyBitcoin(self, usd_amount):
    print(f"Buying ${usd_amount} Bitcoin ...")

    product_id = 'BTC-USD'
    order_result = self.auth_client.place_market_order(product_id, 'buy', funds=usd_amount)
    while not order_result['settled']:
      time.sleep(1)
      order_result = self.auth_client.get_order(order_result['id'])
    self.printOrderResult(order_result)

  def printOrderResult(self, order_result):
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
