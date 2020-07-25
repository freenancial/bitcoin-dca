"""
A global singleton Logger class.
"""
import os
import logging
from logging.handlers import TimedRotatingFileHandler


class Logger:
    """
    A global singleton Logger class.
    """
    _logger = None

    @staticmethod
    def getLogger():
        """
        Get the singleton logger.
        """
        if Logger._logger is None:
            # Prepare log directory
            if not os.path.isdir('log'):
                os.mkdir('log')
            # Prepare the logger
            handler = TimedRotatingFileHandler(
                'log/bitcoin_dca.log', when='midnight', backupCount=365)
            formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
            handler.setFormatter(formatter)
            logger = logging.getLogger("BitcoinDCALogger")
            logger.addHandler(handler)
            logger.setLevel(logging.DEBUG)
            Logger._logger = logger
        return Logger._logger

    @staticmethod
    def debug(message):
        """
        Use the singleton logger to log debug message.
        """
        Logger.getLogger().debug(message)

    @staticmethod
    def info(message):
        """
        Use the singleton logger to log info message.
        """
        Logger.getLogger().info(message)

    @staticmethod
    def warn(message):
        """
        Use the singleton logger to log warning message.
        """
        Logger.getLogger().warn(message)

    @staticmethod
    def error(message):
        """
        Use the singleton logger to log error message.
        """
        Logger.getLogger().error(message)

    @staticmethod
    def critical(message):
        """
        Use the singleton logger to log critical message.
        """
        Logger.getLogger().critical(message)

    @staticmethod
    def setLevel(level):
        """
        Set the logging level of the singleton logger.
        """
        Logger.getLogger().setLevel(level)
