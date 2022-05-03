from flask_login import UserMixin
from dais_pcto.app import db


class Lesson(UserMixin, db.Model):
    __tablename__ = "lessons"

    id = db.Column(db.Integer, primary_key=True)
    start_hour = db.Column(db.TIME, nullable=False)
    end_hour = db.Column(db.TIME, nullable=False)
    date = db.Column(db.TIMESTAMP, nullable=False)
    mode = db.Column(db.Integer, nullable=False)  # modalita 0 = online modalità 1 = presenza modalita 3 = blendend
    link = db.Column(db.String(2083), nullable=False)
    structure = db.Column(db.String(64), nullable=True)  # può essere null esempio lezione solo online
    description = db.Column(db.TEXT, nullable=False, default="Descrizione non ancora disponibile")

    # relazioni
    course = db.Column(db.Integer, db.ForeignKey(
        'courses.id'))

    def __repr__(self):
        return '<Lesson %r>' % self.id
