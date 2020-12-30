# Preparing Shell Script
```
cd bitcoin-dca && source venv/bin/activate && export PYTHONPATH="./bitcoin_dca" && python
```

# Use BitcoinDCA wrapper class
```
import getpass
from bitcoin_dca.bitcoin_dca import BitcoinDCA
passwd = getpass.getpass()

bitcoin_dca = BitcoinDCA(True, passwd)
```

# Use Robinhood class
```
import robin_stocks
import pyotp
username = bitcoin_dca.secrets["robinhood_user"]
passwd = bitcoin_dca.secrets["robinhood_password"]
totp = bitcoin_dca.secrets["robinhood_totp"]
login = robin_stocks.login(username, passwd, mfa_code=pyotp.TOTP(totp).now())
```

# Use CoinbasePro class
```
from coinbase_pro import CoinbasePro
from config import Config

cbpro = CoinbasePro(api_key, api_secret, passphrase, Config("../config.ini"))
```
