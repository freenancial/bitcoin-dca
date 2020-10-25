# Preparing Shell Script
```
cd bitcoin_dca
source venv/bin/activate
export PYTHONPATH="./bitcoin_dca"
python
```

# Use BitcoinDCA wrapper class
```
import getpass
from bitcoin_dca.bitcoin_dca import BitcoinDCA
passwd = getpass.getpass()
bitcoin_dca = BitcoinDCA(passwd)
```

# Use CoinbasePro class
```
from coinbase_pro import CoinbasePro
from config import Config

cbpro = CoinbasePro(api_key, api_secret, passphrase, Config("../config.ini"))
```