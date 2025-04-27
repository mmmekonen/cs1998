import os

import boto3
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

BASE_DIR = os.getcwd()
S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME")
S3_BASE_URL = f"https://{S3_BUCKET_NAME}.s3.us-east-2.amazonaws.com"

# implement database model classes
student_courses = db.Table(
    "student_courses",
    db.Model.metadata,
    db.Column("user_id", db.Integer, db.ForeignKey("users.id")),
    db.Column("course_id", db.Integer, db.ForeignKey("courses.id")),
)

instructor_courses = db.Table(
    "instructor_courses",
    db.Model.metadata,
    db.Column("user_id", db.Integer, db.ForeignKey("users.id")),
    db.Column("course_id", db.Integer, db.ForeignKey("courses.id")),
)


class Course(db.Model):
    """
    Course Model
    """

    __tablename__ = "courses"
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    assignments = db.relationship(
        "Assignment", cascade="delete", back_populates="course"
    )
    instructors = db.relationship(
        "User", secondary=instructor_courses, back_populates="courses"
    )
    students = db.relationship(
        "User", secondary=student_courses, back_populates="courses"
    )

    def __init__(self, **kwargs):
        """
        Initialize Course object
        """
        self.code = kwargs.get("code")
        self.name = kwargs.get("name")

    def serialize(self):
        """
        Serialize a Course object
        """
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "assignments": [a.simple_serialize() for a in self.assignments],
            "instructors": [i.simple_serialize() for i in self.instructors],
            "students": [s.simple_serialize() for s in self.students],
        }

    def simple_serialize(self):
        """
        Serialize a Course object without assignment, instructor, or student fields
        """
        return {"id": self.id, "code": self.code, "name": self.name}


class Assignment(db.Model):
    """
    Assignment Model
    """

    __tablename__ = "assignments"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    due_date = db.Column(db.Integer, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    course = db.relationship("Course", back_populates="assignments")
    submissions = db.relationship(
        "Submission", cascade="delete", back_populates="assignment"
    )

    def __init__(self, **kwargs):
        """
        Initialize an Assignment object
        """
        self.title = kwargs.get("title")
        self.due_date = kwargs.get("due_date")
        self.course_id = kwargs.get("course_id")

    def serialize(self):
        """
        Serialize an Assignment object
        """
        return {
            "id": self.id,
            "title": self.title,
            "due_date": self.due_date,
            "course": self.course.simple_serialize(),
        }

    def simple_serialize(self):
        """
        Serialize an Assignment object without course field
        """
        return {"id": self.id, "title": self.title, "due_date": self.due_date}


class User(db.Model):
    """
    User Model
    """

    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    netid = db.Column(db.String, nullable=False)
    courses = db.relationship(
        "Course",
        secondary=db.union(instructor_courses.select(), student_courses.select()).alias(
            "all_user_courses"
        ),
        viewonly=True,
    )
    submissions = db.relationship("Submission", cascade="delete", back_populates="user")

    def __init__(self, **kwargs):
        """
        Initialize Student object
        """
        self.name = kwargs.get("name")
        self.netid = kwargs.get("netid")

    def serialize(self):
        """
        Serialize a User object
        """
        return {
            "id": self.id,
            "name": self.name,
            "netid": self.netid,
            "courses": [c.simple_serialize() for c in self.courses],
        }

    def simple_serialize(self):
        """
        Serialize a User object without course field
        """
        return {"id": self.id, "name": self.name, "netid": self.netid}


## OPTIONAL TASKS
# TASK 1/3
class Submission(db.Model):
    """
    Submission Model
    """

    __tablename__ = "submissions"
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer)
    content = db.Column(db.String, nullable=False)
    assignment_id = db.Column(
        db.Integer, db.ForeignKey("assignments.id"), nullable=False
    )
    assignment = db.relationship("Assignment", back_populates="submissions")
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("User", back_populates="submissions")

    def __init__(self, **kwargs):
        """
        Initialize Submission object
        """
        self.upload_content(kwargs.get("content"))
        self.assignment_id = kwargs.get("assignment_id")
        self.user_id = kwargs.get("user_id")

    def upload_content(self, content):
        """
        Uploads the submission's file content to s3
        """
        try:
            filename = content[content.rfind("\\") + 1 :]
            s3 = boto3.client("s3")
            s3.upload_file(
                content, S3_BUCKET_NAME, filename, ExtraArgs={"ACL": "public-read"}
            )
            self.content = f"{S3_BASE_URL}/{filename}"
        except Exception as e:
            print(f"Error when uploading file: {e}")

    def serialize(self):
        """
        Serialize a Submission object
        """
        return {
            "id": self.id,
            "score": self.score,
            "content": self.content,
            "user": self.user.simple_serialize(),
            "assignment": self.assignment.simple_serialize(),
        }

    def simple_serialize(self):
        """
        Serialize a Submission object without assignment or user field
        """
        return {"id": self.id, "score": self.score, "content": self.content}
