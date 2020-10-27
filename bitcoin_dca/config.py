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
    def dca_frequency(self):
        dca_times_per_day = self.config["COINBASE_PRO"].getfloat("DCA_TIMES_PER_DAY")
        seconds_per_day = 24 * 3600
        # Convert dca times per day to dca frequency in seconds
        return int(seconds_per_day / dca_times_per_day)

    @property
    def dca_usd_amount(self):
        return self.config["COINBASE_PRO"].getint("DCA_USD_AMOUNT")

    @property
    def min_usdc_balance(self):
        return self.config["COINBASE_PRO"].getfloat("MIN_USDC_BALANCE")

    @property
    def robinhood_dca_frequency(self):
        dca_times_per_day = self.config["ROBINHOOD"].getfloat("DCA_TIMES_PER_DAY")
        seconds_per_day = 24 * 3600
        # Convert dca times per day to dca frequency in seconds
        return int(seconds_per_day / dca_times_per_day)

    @property
    def robinhood_dca_usd_amount(self):
        return self.config["ROBINHOOD"].getfloat("DCA_USD_AMOUNT")

    @property
    def withdraw_every_x_buy(self):
        return self.config["AUTO_WITHDRAWL"].getint("WITHDRAW_EVERY_X_BUY")

    @property
    def withdraw_master_public_key(self):
        return self.config["AUTO_WITHDRAWL"].get("MASTER_PUBLIC_KEY")

    @property
    def withdraw_beginning_address(self):
        return self.config["AUTO_WITHDRAWL"].get("BEGINNING_ADDRESS")

    @property
    def notification_gmail_user_name(self):
        return self.config["NOTIFICATION"].get("GMAIL_USER_NAME")

    @property
    def notification_receiver(self):
        return self.config["NOTIFICATION"].get("EMAIL_NOTICE_RECEIVER")
