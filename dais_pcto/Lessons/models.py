from flask_login import UserMixin
from dais_pcto.app import db
from dais_pcto.Auth.models import user_lesson


class Lesson(UserMixin, db.Model):
    __tablename__ = "lessons"

    _lesson_id = db.Column(db.Integer, primary_key=True)
    _start_hour = db.Column(db.TIME, nullable=False)
    _end_hour = db.Column(db.TIME, nullable=False)
    _date = db.Column(db.DATE, nullable=False)
    _mode = db.Column(db.String(10), nullable=False)  # modalita 0 = online modalità 1 = presenza modalita 3 = blendend
    _link = db.Column(db.String(2083), nullable=False)
    _structure = db.Column(db.String(64), nullable=True)  # può essere null esempio lezione solo online
    _description = db.Column(db.TEXT, nullable=False, default="Descrizione non ancora disponibile")
    _secret_token = db.Column(db.String(32), nullable=False)

    # relazioni
    course = db.Column(db.Integer, db.ForeignKey(
        'courses._course_id'))

    _users = db.relationship("User", secondary=user_lesson,
                             back_populates="_lessons")
    # collegamento molti a molti tra utenti e lezioni per fattore partecipazione alla lezione

    # Costruttore oggetto
    def __init__(self, start_hour, end_hour, date, mode, link, structure, description, course, token):
        self._start_hour = start_hour
        self._end_hour = end_hour
        self._date = date
        self._mode = mode
        self._link = link
        self._structure = structure
        self._description = description
        self.course = course
        self._secret_token = token
