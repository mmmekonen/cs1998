import json

from db import Assignment, Course, Submission, User, db
from flask import Flask, request

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


# helper for writing error messages
def create_message(fields):
    return (
        ", ".join(fields[:-1])
        + (" and " if len(fields) > 1 else "")
        + fields[-1]
        + " not provided."
    )


# -- COURSE ROUTES ----------------------------------------------------


@app.route("/")
def hello_world():
    return success_response("hello world!")


@app.route("/api/courses/")
def get_courses():
    """
    Endpoint for getting all courses
    """
    courses = [c.serialize() for c in Course.query.all()]
    return success_response({"courses": courses})


@app.route("/api/courses/", methods=["POST"])
def create_course():
    """
    Endpoint for creating a new course
    """
    body = json.loads(request.data)
    code = body.get("code")
    name = body.get("name")

    fields = []
    if code is None:
        fields.append("Code")
    if name is None:
        fields.append("Name")
    if fields != []:
        return failure_response(create_message(fields), 400)

    new_course = Course(code=code, name=name)
    db.session.add(new_course)
    db.session.commit()
    return success_response(new_course.serialize(), 201)


@app.route("/api/courses/<int:course_id>/")
def get_course(course_id):
    """
    Endpoint for getting a course by id
    """
    course = Course.query.filter_by(id=course_id).first()
    if course is None:
        return failure_response("Course not found!")
    return success_response(course.serialize())


@app.route("/api/courses/<int:course_id>/", methods=["DELETE"])
def delete_course(course_id):
    """
    Endpoint for deleting a course by id
    """
    course = Course.query.filter_by(id=course_id).first()
    if course is None:
        return failure_response("Course not found!")
    db.session.delete(course)
    db.session.commit()
    return success_response(course.serialize())


# -- USER ROUTES ------------------------------------------------------


@app.route("/api/users/", methods=["POST"])
def create_user():
    """
    Endpoint for creating a user
    """
    body = json.loads(request.data)
    name = body.get("name")
    netid = body.get("netid")

    fields = []
    if name is None:
        fields.append("Name")
    if netid is None:
        fields.append("Netid")
    if fields != []:
        return failure_response(create_message(fields), 400)

    new_user = User(name=name, netid=netid)
    db.session.add(new_user)
    db.session.commit()
    return success_response(new_user.serialize(), 201)


@app.route("/api/users/<int:user_id>/")
def get_user(user_id):
    """
    Endpoint for getting a user by id
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found!")
    return success_response(user.serialize())


@app.route("/api/courses/<int:course_id>/add/", methods=["POST"])
def add_user_to_course(course_id):
    """
    Endpoint for adding a user to a course by id
    """
    course = Course.query.filter_by(id=course_id).first()
    if course is None:
        return failure_response("Course not found!")

    body = json.loads(request.data)
    user_id = body.get("user_id")
    user_type = body.get("type")

    fields = []
    if user_id is None:
        fields.append("User_id")
    if user_type is None:
        fields.append("Type")
    if fields != []:
        return failure_response(create_message(fields), 400)

    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found!")

    if user_type == "student":
        course.students.append(user)
    elif user_type == "instructor":
        course.instructors.append(user)
    else:
        return failure_response("Type must be either 'student' or 'instructor'.", 400)

    db.session.commit()
    return success_response(course.serialize())


# -- ASSIGNMENT ROUTES ------------------------------------------------


@app.route("/api/courses/<int:course_id>/assignment/", methods=["POST"])
def create_assignment(course_id):
    """
    Endpoint for creating an assignment for a course by id
    """
    course = Course.query.filter_by(id=course_id).first()
    if course is None:
        return failure_response("Course not found!")

    body = json.loads(request.data)
    title = body.get("title")
    due_date = body.get("due_date")

    fields = []
    if title is None:
        fields.append("Title")
    if due_date is None:
        fields.append("Due_date")
    if fields != []:
        return failure_response(create_message(fields), 400)

    new_assignment = Assignment(title=title, due_date=due_date, course_id=course_id)
    db.session.add(new_assignment)
    db.session.commit()
    return success_response(new_assignment.serialize(), 201)


## OPTIONAL TASKS
# TASK 1
@app.route("/api/courses/<int:course_id>/drop/", methods=["POST"])
def drop_student(course_id):
    """
    Endpoint for dropping a student from a course
    """
    course = Course.query.filter_by(id=course_id).first()
    if course is None:
        return failure_response("Course not found")

    body = json.loads(request.data)
    user_id = body.get("user_id")
    if user_id is None:
        return failure_response(create_message(["User_id"]), 400)

    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found")

    if user not in course.students:
        return failure_response("User has not been added to this course")

    course.students.remove(user)
    db.session.commit()
    return success_response(user.serialize())


@app.route("/api/assignments/<int:assignment_id>/", methods=["POST"])
def update_assignment(assignment_id):
    """
    Endpoint for updating an assignment by id
    """
    body = json.loads(request.data)
    title = body.get("title")
    due_date = body.get("due_date")

    assignment = Assignment.query.filter_by(id=assignment_id).first()
    if assignment is None:
        return failure_response("Assignment not found")

    if title is None and due_date is None:
        return failure_response("Title or due_date must be provided.", 400)
    if title is not None:
        assignment.title = title
    if due_date is not None:
        assignment.due_date = due_date

    db.session.commit()
    return success_response(assignment.serialize())


# TASK 2
@app.route("/api/assignments/<int:assignment_id>/submit/", methods=["POST"])
def submit_assignment(assignment_id):
    """
    Endpoint for submitting an assignment by id
    """
    assignment = Assignment.query.filter_by(id=assignment_id).first()
    if assignment is None:
        return failure_response("Assignment not found")

    body = json.loads(request.data)
    user_id = body.get("user_id")
    content = body.get("content")
    fields = []
    if user_id is None:
        fields.append("User_id")
    if content is None:
        fields.append("Content")
    if fields != []:
        return failure_response(create_message(fields), 400)

    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found")

    if user not in assignment.course.students:
        return failure_response("User does not have this assignment", 400)

    new_submission = Submission(
        content=content, user_id=user_id, assignment_id=assignment_id
    )
    db.session.add(new_submission)
    db.session.commit()
    return success_response(new_submission.serialize(), 201)


@app.route("/api/assignments/<int:assignment_id>/grade/", methods=["POST"])
def grade_assignment(assignment_id):
    """
    Endpoint for grading an assignment by id
    """
    assignment = Assignment.query.filter_by(id=assignment_id).first()
    if assignment is None:
        return failure_response("Assignment not found")

    body = json.loads(request.data)
    submission_id = body.get("submission_id")
    score = body.get("score")
    fields = []
    if submission_id is None:
        fields.append("Submission_id")
    if score is None:
        fields.append("Score")
    if fields != []:
        return failure_response(create_message(fields), 400)

    submission = Submission.query.filter_by(id=submission_id).first()
    if submission is None:
        return failure_response("Submission not found")

    if submission.assignment != assignment:
        return failure_response("Submission does not match this assignment", 400)

    submission.score = score
    db.session.commit()
    return success_response(submission.serialize())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
