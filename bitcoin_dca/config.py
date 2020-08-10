"""This module defines all the configs for bitcoin_dca.
"""

import configparser


class Config:
    def __init__(self, config_file_path):
        self.config_file_path = config_file_path
        self.config = configparser.ConfigParser()
        self.config.read(config_file_path)

    def reload(self):
        self.config.read(self.config_file_path)

    @property
    def dcaUsdAmount(self):
        return self.config["BASIC"].getint("DCA_USD_AMOUNT")

    @property
    def dcaFrequency(self):
        return self.config["BASIC"].getint("DCA_FREQUENCY")

    @property
    def minUsdcBalance(self):
        return self.config["BASIC"].getfloat("MIN_USDC_BALANCE")

    @property
    def withdrawEveryXBuy(self):
        return self.config["AUTO_WITHDRAWL"].getint("WITHDRAW_EVERY_X_BUY")

    @property
    def withdrawMasterPublicKey(self):
        return self.config["AUTO_WITHDRAWL"].get("MASTER_PUBLIC_KEY")

    @property
    def withdrawBeginningAddress(self):
        return self.config["AUTO_WITHDRAWL"].get("BEGINNING_ADDRESS")

    @property
    def notificationGmailUserName(self):
        return self.config["NOTIFICATION"].get("GMAIL_USER_NAME")

    @property
    def notificationReceiver(self):
        return self.config["NOTIFICATION"].get("EMAIL_NOTICE_RECEIVER")
