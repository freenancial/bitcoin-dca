# Preparing Shell Script:
#
# cd bitcoin_dca
# source venv/bin/activate
# cd bitcoin_dca
# python

from coinbase_pro import CoinbasePro
from config import Config

cbpro = CoinbasePro(api_key, api_secret, passphrase, Config("../config.ini"))
