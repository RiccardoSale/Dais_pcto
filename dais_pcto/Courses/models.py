from sqlalchemy import CheckConstraint

from dais_pcto.app import db
from flask_login import UserMixin
from dais_pcto.Auth.models import user_course


class Course(UserMixin, db.Model):
    __tablename__ = "courses"

    _course_id = db.Column(db.Integer, primary_key=True)
    _name = db.Column(db.String(64), unique=True, nullable=False, index=True)
    _mode = db.Column(db.String(10), nullable=False)  # modalita 0 = online modalità 1 = presenza modalita 3 = blendend
    _description = db.Column(db.TEXT, nullable=False, default="Descrizione non ancora disponibile")
    _max_student = db.Column(db.Integer, CheckConstraint('max_student > min_student', name='max_stud_costr'),
                             nullable=False)
    _min_student = db.Column(db.Integer, CheckConstraint('min_student < max_student', name='min_stud_costr'),
                             nullable=False)
    _n_hour = db.Column(db.Integer, nullable=False)  # DIVENTA RICAVATO

    _start_month = db.Column(db.DATE, CheckConstraint('str(end_month) > str(start_month)', name='start_month_costr'),
                             nullable=False)
    _end_month = db.Column(db.DATE, CheckConstraint('str(start_month) < str(end_month)', name='end_month_costr'),
                           nullable=False)  # da start month o end month ricavo periodo

    # NUMERO LEZIONI STABILITO A PRIORI -> PROGRAMMA SETTIMANA -> 2 LEZIONI NORMALI DA 1 ORA E MEZZA -> 1 LEZIONE SPECIALE DA 3 ORE

    _lessons = db.relationship('Lesson', backref='courses')  # molti a uno dove uno è il corso
    _professor = db.Column(db.Integer, db.ForeignKey(
        'users._user_id',
        ondelete="CASCADE"))  # Chiave esterna professore indica l'utente che è professore che ha creato il corso !
    # ->chiave esterna a utente -> e poi vincolo trigger blocca inserimento e la modifica di un eventuale utente che non abbia ruolo professore

    _users = db.relationship("User", secondary=user_course,
                             back_populates="_courses")  # collegamento molti a molti tra utenti e corsi per fattore iscrizione utente normale

    def __repr__(self):
        return '<Course %r>' % self._name

    # Costruttore oggetto
    def __init__(self, name, mode, description, max_student, min_student, n_hour, start_month, end_month, professor):
        self._name = name
        self._mode = mode
        self._description = description
        self._max_student = max_student
        self._min_student = min_student
        self._n_hour = n_hour
        self._start_month = start_month
        self._end_month = end_month
        self._professor = professor
