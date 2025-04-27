import datetime
import json

import users_dao
from db import db
from flask import Flask, request

db_filename = "auth.db"
app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

db.init_app(app)
with app.app_context():
    db.create_all()


# generalized response formats
def success_response(data, code=200):
    """
    Generalized success response function
    """
    return json.dumps(data), code


def failure_response(message, code=404):
    """
    Generalized failure response function
    """
    return json.dumps({"error": message}), code


def extract_token(request):
    """
    Helper function that extracts the token from the header of a request
    """
    auth_header = request.headers.get("Authorization")
    if auth_header is None:
        return False, failure_response("Missing Authorization header", 400)

    # Bearer <token>
    bearer_token = auth_header.replace("Bearer", "").strip()
    if not bearer_token:
        return False, failure_response("Invalid Authorization header", 400)
    return True, bearer_token


@app.route("/")
def hello_world():
    """
    Endpoint for printing Hello World!
    """
    return success_response({"message": "Hello World!"})


@app.route("/register/", methods=["POST"])
def register_account():
    """
    Endpoint for registering a new user
    """
    body = json.loads(request.data)
    first_name = body.et("first_name")
    email = body.get("email")
    password = body.get("password")

    if first_name is None or email is None or password is None:
        return failure_response("Invaild body", 400)

    created, user = users_dao.create_user(first_name, email, password)
    if not created:
        return failure_response("User already exists")

    return success_response(
        {
            "session_token": user.session_token,
            "session_expiration": str(user.session_expiration),
            "update_token": user.update_token,
        },
        201,
    )


@app.route("/login/", methods=["POST"])
def login():
    """
    Endpoint for logging in a user
    """
    body = json.loads(request.data)
    email = body.get("email")
    password = body.get("password")

    if email is None or password is None:
        return failure_response("Invaild body", 400)

    success, user = users_dao.verify_credentials(email, password)
    if not success:
        return failure_response("Invalid credentials", 401)

    user.renew_session()
    db.session.commit()
    return success_response(
        {
            "session_token": user.session_token,
            "session_expiration": str(user.session_expiration),
            "update_token": user.update_token,
        },
        201,
    )


@app.route("/session/", methods=["POST"])
def update_session():
    """
    Endpoint for updating a user's session
    """
    success, response = extract_token(request)
    if not success:
        return response
    refresh_token = response

    try:
        user = users_dao.renew_session(refresh_token)
    except Exception:
        return failure_response("Invalid update token", 400)

    return success_response(
        {
            "session_token": user.session_token,
            "session_expiration": str(user.session_expiration),
            "update_token": user.update_token,
        },
        201,
    )


@app.route("/secret/", methods=["GET"])
def secret_message():
    """
    Endpoint for verifying a session token and returning a secret message

    In your project, you will use the same logic for any endpoint that needs
    authentication
    """
    success, response = extract_token(request)
    if not success:
        return response
    session_token = response
    user = users_dao.get_user_by_session_token(session_token)
    if not user or not user.verify_session_token(session_token):
        return failure_response("Invalid sesson token", 400)

    return success_response({"message": "hello " + user.first_name})


@app.route("/logout/", methods=["POST"])
def logout():
    """
    Endpoint for logging out a user
    """
    success, response = extract_token(request)
    if not success:
        return response
    session_token = response

    user = users_dao.get_user_by_session_token(session_token)
    if not user or not user.verify_session_token(session_token):
        return failure_response("Invalid session token", 400)
    user.session_expiration = datetime.datetime.now()
    db.session.commit()
    return success_response({"message": "You have been logged out"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
