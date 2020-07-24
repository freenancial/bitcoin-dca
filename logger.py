import os
import logging
from logging.handlers import TimedRotatingFileHandler

class Logger:
    _logger = None

    @staticmethod
    def getLogger():
        if Logger._logger is None:
            # Prepare log directory
            if not os.path.isdir('log'):
                os.mkdir('log')
            # Prepare the logger
            handler = TimedRotatingFileHandler('log/bitcoin_dca.log', when='midnight', backupCount=365)
            formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
            handler.setFormatter(formatter)
            logger = logging.getLogger("BitcoinDCALogger")
            logger.addHandler(handler)
            Logger._logger = logger
        return Logger._logger

    @staticmethod
    def debug(message):
        Logger.getLogger().debug(message)

    @staticmethod
    def info(message):
        Logger.getLogger().info(message)

    @staticmethod
    def warn(message):
        Logger.getLogger().warn(message)

    @staticmethod
    def error(message):
        Logger.getLogger().error(message)

    @staticmethod
    def critical(message):
        Logger.getLogger().critical(message)

    @staticmethod
    def setLevel(level):
        Logger.getLogger().setLevel(level)
