from libpycoin.pycoin.services.providers import spendables_for_address
from libpycoin.pycoin.symbols.btc import network as BTC

class AddressSelector:
    def __init__(self, master_public_key, beginning_address=None):
        self.address_index = 0
        self.receiving_public_key = BTC.parse(master_public_key).subkey_for_path("0")

        if beginning_address is not None:
            for self.address_index in range(1000):
                if self.getCurrentAddress() == beginning_address:
                    break
                self.incrementAddressIndex()
            if self.address_index == 1000:
                raise Exception(f"Unable to find beginning address {beginning_address} with "
                                f"master public key {master_public_key}")

    def getCurrentAddress(self):
        return self.receiving_public_key.subkey_for_path(str(self.address_index)).address()

    def getWithdrawAddress(self):
        while len(spendables_for_address(self.getCurrentAddress(), 'BTC')) > 0:
            print(f"Skip address {self.getCurrentAddress()} since it has already been used.")
            self.incrementAddressIndex()
        return self.getCurrentAddress()

    def incrementAddressIndex(self):
        self.address_index += 1
