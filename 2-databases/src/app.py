import hashlib
import json
import os

import db
from flask import Flask, request

app = Flask(__name__)
DB = db.DatabaseDriver()


def success_response(body, code=200):
    """
    Dumps the given body as json and returns code 200 if one isn't given.
    """
    return json.dumps(body), code


def failure_response(message, code=404):
    """
    Dumps the error message and returns code 404 is one isn't given.
    """
    return json.dumps({"error": message}), code


@app.route("/")
@app.route("/api/users/")
def get_users():
    """
    Returns all users.
    """
    return success_response({"users": DB.get_all_users()})


@app.route("/api/users/", methods=["POST"])
def create_user():
    """
    Creates a new user given a name, username, and optional balance.
    """
    body = json.loads(request.data)
    name = body.get("name")
    username = body.get("username")
    balance = body.get("balance", 0)

    if name is None and username is None:
        return failure_response("Name and username were not provided.", 400)
    elif name is None:
        return failure_response("Name waw not provided.", 400)
    elif username is None:
        return failure_response("Username was not provided.", 400)

    user_id = DB.insert_user(name, username, balance)
    user = DB.get_user_by_id(user_id)
    if user is None:
        return failure_response("Something went wrong while creating the user!", 500)
    return success_response(user, 201)


@app.route("/api/user/<int:user_id>/")
def get_user(user_id):
    """
    Returns the user specified by the given id.
    """
    user = DB.get_user_by_id(user_id)
    if user is None:
        return failure_response("User not found.")
    return success_response(user)


@app.route("/api/user/<int:user_id>/", methods=["DELETE"])
def delete_user(user_id):
    """
    Deletes the user specified by the given id.
    """
    user = DB.get_user_by_id(user_id)
    if user is None:
        return failure_response("User not found.")
    DB.delete_user_by_id(user_id)
    return success_response(user)


@app.route("/api/send/", methods=["POST"])
def send_money():
    """
    Sends the specified amount of money from one user to another.
    """
    body = json.loads(request.data)
    sender_id = body.get("sender_id")
    receiver_id = body.get("receiver_id")
    amount = body.get("amount")

    message = []
    if sender_id is None:
        message.append("sender_id")
    if receiver_id is None:
        message.append("receiver_id")
    if amount is None:
        message.append("amount")
    if message != []:
        return failure_response(
            (
                ", ".join(message[:-1])
                + (" and " if len(message) > 1 else "")
                + message[-1]
                + " not provided."
            ),
            400,
        )

    sender = DB.get_user_by_id(sender_id)
    if sender["balance"] < amount:
        return failure_response("Sender does not have enough balance", 400)

    DB.send_money_to_user(sender_id, receiver_id, amount)
    return success_response(body)


# OPTIONAL TASKS
# TASK 1
@app.route("/api/extra/users/", methods=["POST"])
def create_user_w_password():
    """
    Creates a new user given a name, username, password, and optional balance.
    """
    body = json.loads(request.data)
    name = body.get("name")
    username = body.get("username")
    balance = body.get("balance", 0)
    password = body.get("password")

    if name is None and username is None:
        return failure_response("Name and username were not provided.", 400)
    elif name is None:
        return failure_response("Name waw not provided.", 400)
    elif username is None:
        return failure_response("Username was not provided.", 400)
    if password is None:
        return failure_response("Password must be provided.", 401)

    # user_id = DB.insert_user(name, username, balance, hash_password(password))
    user_id = DB.insert_user(name, username, balance, hash_password_salt(password))
    user = DB.get_user_by_id(user_id)
    if user is None:
        return failure_response("Something went wrong while creating the user!", 500)
    return success_response(user, 201)


@app.route("/api/extra/user/<int:user_id>/", methods=["POST"])
def get_user_w_password(user_id):
    """
    Returns the user specified by the given id if correct password is given.
    """
    body = json.loads(request.data)
    password = body.get("password")

    if password is None:
        return failure_response("Password must be provided.", 401)

    user = DB.get_user_by_id(user_id)
    if user is None:
        return failure_response("User not found.")
    # if hash_password(password) != DB.get_user_password(user_id)["password"]:
    if hash_password_salt(password) != DB.get_user_password(user_id)["password"]:
        return failure_response("Incorrect password.", 401)
    return success_response(user)


@app.route("/api/extra/send/", methods=["POST"])
def send_money_w_password():
    """
    Sends the specified amount of money from one user to another. Requires sender's password.
    """
    body = json.loads(request.data)
    sender_id = body.get("sender_id")
    receiver_id = body.get("receiver_id")
    amount = body.get("amount")
    password = body.get("sender_password")

    message = []
    if sender_id is None:
        message.append("sender_id")
    if receiver_id is None:
        message.append("receiver_id")
    if amount is None:
        message.append("amount")
    if message != []:
        return failure_response(
            (
                ", ".join(message[:-1])
                + (" and " if len(message) > 1 else "")
                + message[-1]
                + " not provided."
            ),
            400,
        )

    if password is None:
        return failure_response("Sender password must be provided.", 401)

    # if hash_password(password) != DB.get_user_password(sender_id)["password"]:
    if hash_password_salt(password) != DB.get_user_password(sender_id)["password"]:
        return failure_response("Incorrect password.", 401)

    sender = DB.get_user_by_id(sender_id)
    if sender["balance"] < amount:
        return failure_response("Sender does not have enough balance", 400)

    DB.send_money_to_user(sender_id, receiver_id, amount)
    return success_response(body)


# TASK 2
def hash_password(password):
    """
    Returns the hashed version of the given password.
    """
    return hashlib.sha256(password.encode()).hexdigest()


# TASK 3
def hash_password_salt(password):
    """
    Returns the hashed password using salting and iterative hashing.
    """
    password += os.getenv("PASSWORD_SALT")
    for i in range(int(os.getenv("NUMBER_OF_ITERATIONS"))):
        password = hashlib.sha256(password.encode()).hexdigest()
    return password


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
