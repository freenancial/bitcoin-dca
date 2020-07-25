import sqlite3

DB_NAME = 'bitcoin_dca.db'


class DBManager:
    def __init__(self):
        self.conn = sqlite3.connect(DB_NAME)
        self.initTables()

    def initTables(self):
        c = self.conn.cursor()
        c.execute('''CREATE TABLE if not exists BuyOrders
                     (date text, cost real, size real, withdraw_address text)''')
        self.conn.commit()

    def saveBuyTransaction(self, date, cost, size):
        c = self.conn.cursor()
        c.execute(f'''
            INSERT INTO BuyOrders VALUES ('{date}', {cost}, {size}, '')
        ''')
        self.conn.commit()

    def updateWithdrawAddressForBuyOrders(self, withdraw_address):
        c = self.conn.cursor()
        c.execute(f'''
            UPDATE BuyOrders
            SET withdraw_address = '{withdraw_address}'
            WHERE withdraw_address = ''
        ''')
        self.conn.commit()

    def getUnwithdrawnBuysCount(self):
        c = self.conn.cursor()
        c.execute('''
            SELECT COUNT(*) from BuyOrders
            WHERE withdraw_address = ''
        ''')
        return c.fetchone()[0]

    def getUnwithdrawnBuyOrders(self):
        c = self.conn.cursor()
        c.execute('''
            SELECT date, cost, size from BuyOrders
            WHERE withdraw_address = ''
        ''')
        return list(c)

    def printAllBuyTransactions(self):
        c = self.conn.cursor()
        c.execute('''
            SELECT * from BuyOrders
        ''')
        for buy_order in c:
            print(buy_order)
