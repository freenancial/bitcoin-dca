import sqlite3
from datetime import datetime, timezone

DB_NAME = "bitcoin_dca.db"


class DBManager:
    def __init__(self):
        self.conn = sqlite3.connect(DB_NAME)
        self.initTables()

    def initTables(self):
        c = self.conn.cursor()
        c.execute(
            """
            CREATE TABLE if not exists BuyOrders
            (date text, cost real, size real, withdraw_address text)
            """
        )
        self.conn.commit()

    def saveBuyTransaction(self, date, cost, size):
        c = self.conn.cursor()
        c.execute(
            f"""
            INSERT INTO BuyOrders VALUES ('{date}', {cost}, {size}, '')
            """
        )
        self.conn.commit()

    def updateWithdrawAddressForBuyOrders(self, withdraw_address):
        c = self.conn.cursor()
        c.execute(
            f"""
            UPDATE BuyOrders
            SET withdraw_address = '{withdraw_address}'
            WHERE withdraw_address = ''
            """
        )
        self.conn.commit()

    def getUnwithdrawnBuysCount(self):
        c = self.conn.cursor()
        c.execute(
            """
            SELECT COUNT(*) FROM BuyOrders
            WHERE withdraw_address = ''
            """
        )
        return c.fetchone()[0]

    def getUnwithdrawnBuyOrders(self):
        c = self.conn.cursor()
        c.execute(
            """
            SELECT date, cost, size FROM BuyOrders
            WHERE withdraw_address = ''
            """
        )
        return list(c)

    def getLastBuyOrderDatetime(self):
        c = self.conn.cursor()
        c.execute(
            """
            SELECT MAX(date) FROM BuyOrders
            """
        )
        return c.fetchone()[0]

    def printAllBuyTransactions(self):
        c = self.conn.cursor()
        c.execute(
            """
            SELECT * FROM BuyOrders
            """
        )
        for buy_order in c:
            print(buy_order)

    @staticmethod
    def convertOrderDatetime(order_datetime):
        utc_datetime = datetime.strptime(order_datetime, "%Y-%m-%dT%H:%M:%S.%fZ")
        local_datetime = utc_datetime.replace(tzinfo=timezone.utc).astimezone(tz=None)
        return local_datetime
