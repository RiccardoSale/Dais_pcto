from flask_login import UserMixin
from dais_pcto.app import db

user_course = db.Table('user_corse',
                       db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                       db.Column('course_id', db.Integer, db.ForeignKey('course.id'))
                       )


class User(UserMixin, db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(200), nullable=False)
    courses = db.relationship("Course", secondary=user_course, back_populates="users")
    role = db.Column(db.String(120), nullable=False, default="user")

    def __repr__(self):
        return '<User %r>' % self.username
