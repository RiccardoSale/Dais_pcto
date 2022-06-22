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

    _start_date = db.Column(db.DATE, CheckConstraint('str(end_date) > str(start_date)', name='start_date_costr'),
                             nullable=False)
    _end_date = db.Column(db.DATE, CheckConstraint('str(start_date) < str(end_date)', name='end_date_costr'),
                           nullable=False)  # da start month o end month ricavo periodo

    # NUMERO LEZIONI STABILITO A PRIORI -> PROGRAMMA SETTIMANA -> 2 LEZIONI NORMALI DA 1 ORA E MEZZA -> 1 LEZIONE SPECIALE DA 3 ORE

    _lessons = db.relationship('Lesson', backref='courses', cascade="all, delete")  # molti a uno dove uno è il corso

    _professor = db.Column(db.Integer, db.ForeignKey(
        'users._user_id'))

    # Chiave esterna professore indica l'utente che è professore che ha creato il corso !
    # ->chiave esterna a utente -> e poi vincolo trigger blocca inserimento e la modifica di un eventuale utente che non abbia ruolo professore

    _users = db.relationship("User", secondary=user_course,
                             back_populates="_courses", )

    # collegamento molti a molti tra utenti e corsi per fattore iscrizione utente normale
    # Quando rimuovo rimosso collegamento in automatico

    def __repr__(self):
        return '<Course %r>' % self._name

    # Costruttore oggetto
    def __init__(self, name, mode, description, max_student, min_student, n_hour, start_date, end_date, professor):
        self._name = name
        self._mode = mode
        self._description = description
        self._max_student = max_student
        self._min_student = min_student
        self._n_hour = n_hour
        self._start_date = start_date
        self._end_date = end_date
        self._professor = professor

    def set_name(self, name):
        if name != "":
            self._name = name

    def set_description(self, description):
        if description != "":
            self._description = description

    def set_max_student(self, max_student):
        if max_student is not None:
            self._max_student = max_student

    def set_n_hour(self, n_hour):
        if n_hour is not None:
            self._n_hour = n_hour

    def set_start_date(self, start_date):
        if start_date is not None:
            self._start_date = start_date

    def set_end_date(self, end_date):
        if end_date is not None:
            self._end_date = end_date



def course_with_id(id):
    return db.session.query(Course).filter_by(_course_id=id)

def courses_with_name(name):
    return db.session.query(Course).filter_by(_name=name)

def courses_with_professor(professor):
    return db.session.query(Course).filter_by(_professor=professor)