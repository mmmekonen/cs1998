from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# implement database model classes


class Course(db.Model):
    """
    Course Model
    """

    __tablename__ = "courses"
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)

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
        return {"id": self.id, "code": self.code, "name": self.name}


class Assignment(db.Model):
    """
    Assignment Model
    """

    __tablename__ = "assignments"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    due_date = db.Column(db.Integer, nullable=False)

    def __init__(self, **kargs):
        """
        Initialize an Assignment object
        """
        self.title = kwargs.get("title")
        self.due_date = kwargs.get("due_date")

    def serialize(self):
        """
        Serialize an Assignment object
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
        return {"id": self.id, "name": self.name, "netid": self.netid}
