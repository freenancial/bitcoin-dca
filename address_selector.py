from pycoin.services.providers import spendables_for_address

class AddressSelector:
    def __init__(self, addresses=[]):
        self.address_index = 0
        self.addresses = addresses

    def getWithdrawAddress(self):
        while self.address_index < len(self.addresses) and len(spendables_for_address(self.addresses[self.address_index], 'BTC')) > 0:
            print(f"Skip address {self.addresses[self.address_index]} since it has already been used.")
            self.address_index += 1
        return self.addresses[self.address_index] if self.address_index < len(self.addresses) else None

    def incrementIndex(self):
        self.address_index += 1
