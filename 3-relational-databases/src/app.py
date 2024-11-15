import json
from flask import Flask, request
import db
import hashlib
from datetime import datetime
from sqlite3 import IntegrityError

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
        return failure_response("Name was not provided.", 400)
    elif username is None:
        return failure_response("Username was not provided.", 400)

    user_id = DB.insert_user(name, username, balance)
    user = DB.get_user_by_id(user_id)
    if user is None:
        return failure_response("Something went wrong while creating the user!", 500)
    return success_response(user, 201)


@app.route("/api/users/<int:user_id>/")
def get_user(user_id):
    """
    Returns the user specified by the given id.
    """
    user = DB.get_user_by_id(user_id)
    if user is None:
        return failure_response("User not found.")
    return success_response(user)


@app.route("/api/users/<int:user_id>/", methods=["DELETE"])
def delete_user(user_id):
    """
    Deletes the user specified by the given id.
    """
    user = DB.get_user_by_id(user_id)
    if user is None:
        return failure_response("User not found.")
    DB.delete_user_by_id(user_id)
    return success_response(user)


@app.route("/api/transactions/", methods=["POST"])
def create_transaction():
    """
    Creates a new transaction with given info.
    """
    body = json.loads(request.data)
    sender_id = body.get("sender_id")
    receiver_id = body.get("receiver_id")
    amount = body.get("amount")
    message = body.get("message")
    accepted = body.get("accepted")

    error_message = []
    if sender_id is None:
        error_message.append("sender_id")
    if receiver_id is None:
        error_message.append("receiver_id")
    if amount is None:
        error_message.append("amount")
    if message is None:
        error_message.append("message")
    if error_message != []:
        return failure_response(
            (
                ", ".join(message[:-1])
                + (" and " if len(message) > 1 else "")
                + message[-1]
                + " not provided."
            ),
            400,
        )

    time = str(datetime.now())
    try:
        transaction = {
            "id": DB.insert_transaction(
                time, sender_id, receiver_id, amount, message, accepted
            ),
            "timestamp": time,
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "amount": amount,
            "message": message,
            "accepted": accepted,
        }
        if accepted:
            sender = DB.get_user_by_id(sender_id)
            if sender["balance"] < amount:
                return failure_response("Sender does not have enough balance", 403)
            DB.send_money_to_user(sender_id, receiver_id, amount)
        return success_response(transaction, 201)
    except IntegrityError:
        return failure_response("One or more users not found.")


@app.route("/api/transactions/<int:transaction_id>/", methods=["POST"])
def accept_or_deny_request(transaction_id):
    """
    Accepts or denys a payment requestion of the given transaction id.
    """
    body = json.loads(request.data)
    accepted = body.get("accepted")

    if accepted is None:
        return failure_response("Accepted field not provided.", 400)

    transaction = DB.get_transaction_by_id(transaction_id)
    if transaction is None:
        return failure_response("Transaction not found.")

    if transaction["accepted"] is None:
        time = str(datetime.now())
        if accepted:
            sender = DB.get_user_by_id(transaction["sender_id"])
            if sender["balance"] < transaction["amount"]:
                return failure_response("Sender does not have enough balance", 403)
            DB.send_money_to_user(
                transaction["sender_id"],
                transaction["receiver_id"],
                transaction["amount"],
            )
            DB.update_transaction_by_id(transaction_id, time, True)
        else:
            DB.update_transaction_by_id(transaction_id, time, False)
    else:
        return failure_response(
            "Cannot change transaction's accepted field if the transaction has already been accepted or denied.",
            403,
        )

    return success_response(DB.get_transaction_by_id(transaction_id))


# OPTIONAL TASKS
# TASK 1
@app.route("/api/extra/users/<int:user_id>/friends/")
def get_friends(user_id):
    """
    Returns the user's friends.
    """
    user = DB.get_user_by_id(user_id)
    if user is None:
        return failure_response("User not found.")
    return success_response({"friends": DB.get_friends_by_user(user_id)})


@app.route("/api/extra/users/<int:user_id>/friends/<int:friend_id>/", methods=["POST"])
def add_friend(user_id, friend_id):
    try:
        DB.insert_friend(user_id, friend_id)
        return success_response("", 201)
    except IntegrityError:
        return failure_response("One or more users not found.")


# TASK 2
@app.route("/api/extra/users/<int:id>/join/")
def get_join_transactions(id):
    """
    Returns the transactions of the given user.
    """
    user = DB.get_user_by_id(id)
    if user is None:
        return failure_response("User not found.")
    return success_response({"transactions": DB.join_query(id)})


# DEPRECATED
# @app.route("/api/send/", methods=["POST"])
# def send_money():
#    """
#    Sends the specified amount of money from one user to another.
#    """
#    body = json.loads(request.data)
#    sender_id = body.get("sender_id")
#    receiver_id = body.get("receiver_id")
#    amount = body.get("amount")
#
#    message = []
#    if sender_id is None:
#        message.append("sender_id")
#    if receiver_id is None:
#        message.append("receiver_id")
#    if amount is None:
#        message.append("amount")
#    if message != []:
#        return failure_response(
#            (
#                ", ".join(message[:-1])
#                + (" and " if len(message) > 1 else "")
#                + message[-1]
#                + " not provided."
#            ),
#            400,
#        )
#
#    sender = DB.get_user_by_id(sender_id)
#    if sender["balance"] < amount:
#        return failure_response("Sender does not have enough balance", 400)
#
#    DB.send_money_to_user(sender_id, receiver_id, amount)
#    return success_response(body)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
