import os
import sqlite3


# From: https://goo.gl/YzypOI
def singleton(cls):
    instances = {}

    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]

    return getinstance


class DatabaseDriver(object):
    """
    Database driver for the Task app.
    Handles with reading and writing data with the database.
    """

    def __init__(self):
        self.conn = sqlite3.connect("venmo.db", check_same_thread=False)
        self.conn.execute("PRAGMA foreign_keys = 1")
        self.create_user_table()
        self.create_transactions_table()

    def create_user_table(self):
        try:
            self.conn.execute(
                """
                CREATE TABLE user (
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    NAME TEXT NOT NULL,
                    USERNAME TEXT NOT NULL,
                    BALANCE INTEGER NOT NULL
                );
                """
            )
        except Exception as e:
            print(e)

    def create_transactions_table(self):
        try:
            self.conn.execute(
                """
                CREATE TABLE transactions (
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    TIMESTAMP TEXT NOT NULL,
                    SENDER_ID INTEGER NOT NULL,
                    RECEIVER_ID INTEGER NOT NULL,
                    AMOUNT INTEGER NOT NULL,
                    MESSAGE TEXT NOT NULL,
                    ACCEPTED BOOLEAN,
                    FOREIGN KEY(SENDER_ID) REFERENCES user(ID),
                    FOREIGN KEY(RECEIVER_ID) REFERENCES user(ID)
                );
                """
            )
        except Exception as e:
            print(e)

    def get_all_users(self):
        """
        Returns a list of all the users in the database.
        """
        cursor = self.conn.execute("SELECT * FROM user;")
        users = []
        for row in cursor:
            users.append({"id": row[0], "name": row[1], "username": row[2]})
        return users

    def insert_user(self, name, username, balance):
        """
        Inserts a user into the db with the given name, username, and balance.
        """
        cursor = self.conn.execute(
            "INSERT INTO user (NAME, USERNAME, BALANCE) VALUES (?,?,?);",
            (name, username, balance),
        )
        self.conn.commit()
        return cursor.lastrowid

    def insert_transaction(
        self, timestamp, sender_id, receiver_id, amount, message, accepted
    ):
        """
        Inserts a transaction into the db with the given info.
        """
        cursor = self.conn.execute(
            "INSERT INTO transactions (TIMESTAMP, SENDER_ID, RECEIVER_ID, AMOUNT, MESSAGE, ACCEPTED) VALUES (?,?,?,?,?,?);",
            (timestamp, sender_id, receiver_id, amount, message, accepted),
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_user_by_id(self, id):
        """
        Returns the user specified by the given id.
        """
        cursor = self.conn.execute("SELECT * FROM user WHERE id = ?;", (id,))
        user = None
        for row in cursor:
            user = {"id": row[0], "name": row[1], "username": row[2], "balance": row[3]}

        if user:
            user["transactions"] = self.get_transactions_by_user(id)
        return user

    def get_transactions_by_user(self, user_id):
        """
        Returns all of the transactions of a user.
        """
        cursor = self.conn.execute(
            "SELECT * FROM transactions WHERE sender_id = ? OR receiver_id = ?;",
            (user_id, user_id),
        )
        transactions = []
        for row in cursor:
            transactions.append(
                {
                    "id": row[0],
                    "timestamp": row[1],
                    "sender_id": row[2],
                    "receiver_id": row[3],
                    "amount": row[4],
                    "message": row[5],
                    "accepted": row[6],
                }
            )
        return transactions

    def delete_user_by_id(self, id):
        """
        Deletes the specified user from the db.
        """
        self.delete_transactions_by_user(id)
        self.conn.execute("DELETE FROM user WHERE id = ?;", (id,))
        self.conn.commit()

    def delete_transactions_by_user(self, user_id):
        """
        Deletes the transactions of the specified user from the db.
        """
        self.conn.execute(
            "DELETE FROM transactions WHERE sender_id = ? OR receiver_id = ?;",
            (user_id, user_id),
        )
        self.conn.commit()

    def send_money_to_user(self, sender_id, receiver_id, amount):
        """
        Increments the balance of the specified user in the db.
        """
        self.conn.execute(
            "UPDATE user SET balance = balance - ? WHERE id = ?;", (amount, sender_id)
        )
        self.conn.execute(
            "UPDATE user SET balance = balance + ? WHERE id = ?;", (amount, receiver_id)
        )
        self.conn.commit()

    def get_transaction_by_id(self, id):
        """
        Returns the transaction with specified id.
        """
        cursor = self.conn.execute("SELECT * FROM transactions WHERE id = ?;", (id,))
        for row in cursor:
            return {
                "id": row[0],
                "timestamp": row[1],
                "sender_id": row[2],
                "receiver_id": row[3],
                "amount": row[4],
                "message": row[5],
                "accepted": row[6],
            }
        return None

    def update_transaction_by_id(self, id, timestamp, accepted):
        """
        Updates the timestamp and accepted fields of the specified transaction.
        """
        self.conn.execute(
            """
            UPDATE transactions
            SET timestamp = ?, accepted = ?
            WHERE id = ?;
        """,
            (timestamp, accepted, id),
        )
        self.conn.commit()


# Only <=1 instance of the database driver
# exists within the app at all times
DatabaseDriver = singleton(DatabaseDriver)
