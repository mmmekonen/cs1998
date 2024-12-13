from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

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
