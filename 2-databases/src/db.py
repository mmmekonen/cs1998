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
        self.create_user_table()
        self.create_password_table()

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

    def get_user_by_id(self, id):
        """
        Returns the user specified by the given id.
        """
        cursor = self.conn.execute("SELECT * FROM user WHERE id = ?;", (id,))
        for row in cursor:
            return {"id": row[0], "name": row[1], "username": row[2], "balance": row[3]}
        return None

    def delete_user_by_id(self, id):
        """
        Deletes the specified user from the db.
        """
        self.conn.execute("DELETE FROM user WHERE id = ?;", (id,))
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

    # OPTIONAL TASKS
    # TASK 1
    def create_password_table(self):
        try:
            self.conn.execute(
                """
                CREATE TABLE password (
                    USER_ID INTEGER PRIMARY KEY,
                    PASSWORD TEXT NOT NULL,
                    FOREIGN KEY (USER_ID) REFERENCES user(ID)
                );
                """
            )
        except Exception as e:
            print(e)

    def insert_user(self, name, username, balance, password):
        """
        Inserts a user into the db with the given name, username, balance, and password.
        """
        cursor = self.conn.execute(
            "INSERT INTO user (NAME, USERNAME, BALANCE) VALUES (?,?,?);",
            (name, username, balance),
        )
        self.conn.execute(
            "INSERT INTO password (USER_ID, PASSWORD) VALUES (?,?)",
            (cursor.lastrowid, password),
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_user_password(self, id):
        """
        Returns the user's password.
        """
        cursor = self.conn.execute("SELECT * FROM password WHERE user_id = ?", (id,))

        for row in cursor:
            return {"user_id": row[0], "password": row[1]}
        return None


# Only <=1 instance of the database driver
# exists within the app at all times
DatabaseDriver = singleton(DatabaseDriver)
