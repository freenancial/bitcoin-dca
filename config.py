# How many dollar of Bitcoin you want to buy each time.
DCA_USD_AMOUNT = 5
# How frequent you want to buy Bitcoin in seconds.
DCA_FREQUENCY = 4320

# If set to True, bitcoin-dca will auto withdraw Bitcoin once the Bitcoin's dollar
# worth of the account is above WITHDRAW_THRESHOLD.
AUTO_WITHDRAWL = False
# Auto withdraw threshold of BTC's dollar worth in the account.
WITHDRAW_THRESHOLD = 98
# The master public key to derive BTC addresess that utilized in auto withdraw.
# Only addresses with empty balance wil be used, and each address will be used
# only once.
MASTER_PUBLIC_KEY = 'xpubxxx'
# The beginning address that BTC auto withdraw to. If set to None, the first address
# derived from MASTER_PUBLIC_KEY will be used as the BEGINNING_ADDRESS.
BEGINNING_ADDRESS = None
