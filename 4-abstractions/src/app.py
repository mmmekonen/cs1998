import json

from db import db
from flask import Flask

# define db filename
db_filename = "cms.db"
app = Flask(__name__)

# setup config
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_filename}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

# initialize app
db.init_app(app)
with app.app_context():
    db.create_all()


# generalized response formats
def success_response(data, code=200):
    return json.dumps(data), code


def failure_response(message, code=404):
    return json.dumps({"error": message}), code


# -- COURSE ROUTES ----------------------------------------------------


@app.route("/")
@app.route("/api/courses/")
def get_courses():
    """
    Endpoint for getting all courses
    """
    pass


@app.route("/api/courses/", methods=["POST"])
def create_course():
    """
    Endpoint for creating a new course
    """
    pass


@app.route("/api/courses/<int:course_id>/")
def get_course(course_id):
    """
    Endpoint for getting a course by id
    """
    pass


@app.route("/api/courses/<int:course_id>/", methods=["DELETE"])
def delete_course(course_id):
    """
    Endpoint for deleting a course by id
    """
    pass


# -- USER ROUTES ------------------------------------------------------


@app.route("/api/users/", methods=["POST"])
def create_user():
    """
    Endpoint for creating a user
    """
    pass


@app.route("/api/users/<int:user_id>/")
def get_user(user_id):
    """
    Endpoint for getting a user by id
    """
    pass


@app.route("/api/courses/<int:course_id>/add/", methods=["POST"])
def add_user_to_course(course_id):
    """
    Endpoint for adding a user to a course by id
    """
    pass


# -- ASSIGNMENT ROUTES ------------------------------------------------


@app.route("/api/courses/<int:course_id>/assignment/", methods=["POST"])
def create_assignment(course_id):
    """
    Endpoint for creating an assignment for a course by id
    """
    pass


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
