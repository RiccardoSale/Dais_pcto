from . import db
from flask_login import UserMixin  # per mantenere la sessione degli utenti attraverso flask login


class User(UserMixin, db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username


# ruolo studente / professore dove lo salviamo come effettuiamo il login ???-> in base a cosa determiniamo il ruolo???


class Courses(UserMixin, db.Model):
    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    department = db.Column(db.String(120), unique=False, nullable=False)
    professor = db.Column(db.String(120), unique=False, nullable=False)

    def __repr__(self):
        return '<Course %r>' % self.name
