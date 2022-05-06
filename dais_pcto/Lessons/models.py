from flask_login import UserMixin
from dais_pcto.app import db


class Lesson(UserMixin, db.Model):
    __tablename__ = "lessons"

    _lesson_id = db.Column(db.Integer, primary_key=True)
    _start_hour = db.Column(db.TIME, nullable=False)
    _end_hour = db.Column(db.TIME, nullable=False)
    _date = db.Column(db.TIMESTAMP, nullable=False)
    _mode = db.Column(db.Integer, nullable=False)  # modalita 0 = online modalità 1 = presenza modalita 3 = blendend
    _link = db.Column(db.String(2083), nullable=False)
    _structure = db.Column(db.String(64), nullable=True)  # può essere null esempio lezione solo online
    _description = db.Column(db.TEXT, nullable=False, default="Descrizione non ancora disponibile")

    # relazioni
    course = db.Column(db.Integer, db.ForeignKey(
        'courses._course_id'))

    def __repr__(self):
        return '<Lesson %r>' % self.id

    # Costruttore oggetto
    def __init__(self, start_hour, end_hour, date, mode, link, structure, description):
        self._start_hour = start_hour
        self._end_hour = end_hour
        self._date = date
        self._mode = mode
        self._link = link
        self._structure = structure
        self._description = description
