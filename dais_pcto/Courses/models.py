from dais_pcto.app import db
from flask_login import UserMixin
from dais_pcto.Auth.models import user_course


class Course(UserMixin, db.Model):
    __tablename__ = "course"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False, index=True)
    department = db.Column(db.String(120), unique=False, nullable=False)
    professor = db.Column(db.String(120), unique=False, nullable=False)
    users = db.relationship("User", secondary=user_course, back_populates="courses")

    def __repr__(self):
        return '<Course %r>' % self.name
