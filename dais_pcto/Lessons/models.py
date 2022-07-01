from flask_login import UserMixin
from dais_pcto.app import db
from dais_pcto.Auth.models import user_lesson


class Lesson(UserMixin, db.Model):
    __tablename__ = "lessons"
    _lesson_id = db.Column(db.Integer, primary_key=True)
    _start_hour = db.Column(db.TIME, nullable=False)
    _end_hour = db.Column(db.TIME, nullable=False)
    _date = db.Column(db.DATE, nullable=False)
    _mode = db.Column(db.String(10), nullable=False)
    _link = db.Column(db.String(2083), nullable=False)
    _structure = db.Column(db.String(64), nullable=True)
    _description = db.Column(db.TEXT, nullable=False, default="Descrizione non ancora disponibile")
    _secret_token = db.Column(db.String(32), nullable=False)

    # Chiave esterna derivata dalla relazione uno a molti con lezioni
    # Una lezione è associata a un corso, un corso ha associate più lezioni
    course = db.Column(db.Integer, db.ForeignKey(
        'courses._course_id'))

    # Collegamento nato dalla relazione molti a molti con gli utenti (con ruolo 'user')
    _users = db.relationship("User", secondary=user_lesson,
                             back_populates="_lessons")

    # Inizializzazione
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

    # Settaggio ora di inizio lezione
    def set_start_hour(self, start_hour):
        if start_hour is not None:
            self._start_hour = start_hour

    # Settaggio ora di fine lezione
    def set_end_hour(self, end_hour):
        if end_hour is not None:
            self._end_hour = end_hour

    # Settaggio della modalità
    def set_mode(self, mode):
        if mode is not None:
            self._mode = mode

    # Settaggio del link
    def set_link(self, link):
        if link != "":
            if link == "vuoto":
                self._link = ""
            else:
                self._link = link

    # Settaggio della struttura
    def set_structure(self, structure):
        if structure != "":
            if structure == "vuoto":
                self._structure = ""
            else:
                self._structure = structure

    # Settaggio della descrizione
    def set_description(self, description):
        if description != "":
            self._description = description

# Ritorno della lezione con un determinato id
def lesson_with_id(id):
    return db.session.query(Lesson).filter_by(_lesson_id=id)

