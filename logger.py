import os
import logging
from logging.handlers import TimedRotatingFileHandler

class Logger:
    def __init__(self, log_level = logging.DEBUG):
        # Prepare log directory
        if not os.path.isdir('log'):
            os.mkdir('log')
        # Prepare the logger
        handler = TimedRotatingFileHandler('log/bitcoin_dca.log', when='midnight', backupCount=365)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        handler.setFormatter(formatter)
        logger = logging.getLogger("BitcoinDCALogger")
        logger.addHandler(handler)
        logger.setLevel(log_level)
        self.logger = logger

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warn(self, message):
        self.logger.warn(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)