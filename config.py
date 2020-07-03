# How many dollar of Bitcoin you want to buy each time.
DCA_USD_AMOUNT = 5
# How frequent you want to buy Bitcoin in seconds.
DCA_FREQUENCY = 4320

# If set to True, bitcoin-dca will auto withdraw Bitcoin to configured BTC_ADDRESSES
# once the Bitcoin worth of the account is above WITHDRAW_THRESHOLD.
AUTO_WITHDRAWL = False
# Once the BTC worth reached the WITHDRAW_THRESHOLD, BTC will be auto withdrew
# to configured BTC_ADDRESSES.
WITHDRAW_THRESHOLD = 100
# A list of BTC addreses for auto withdraw, each address will be used only once.
# When the list is exhausted, the auto withdraw will stop.
BTC_ADDRESSES = [
    "address1",
    "address2",
    "address3",
    "address4",
    "address5",
]
