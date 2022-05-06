from flask_login import UserMixin
from dais_pcto.app import db

user_course = db.Table('user_corse',
                       db.Column('user_id', db.Integer, db.ForeignKey('users._user_id')),
                       db.Column('course_id', db.Integer, db.ForeignKey('courses._course_id'))
                       )


# tabella secondaria per relazione molti a molti tra utenti e corsi


class User(UserMixin, db.Model):
    __tablename__ = "users"

    _user_id = db.Column(db.Integer, primary_key=True)
    _name = db.Column(db.String(64), unique=False, nullable=False)
    _surname = db.Column(db.String(64), unique=False, nullable=False)
    _email = db.Column(db.String(60), unique=True, nullable=False, index=True)
    _password = db.Column(db.String(128),
                          nullable=False)  # lunghezza dopo hashing CONTROLLARE DOPO AVER LIMITATO PASSWORD A TOT CARATTERI
    # cambiare form iscrizione aggiungendo campo choice -> con scuole !!!
    _role = db.Column(db.String(10), nullable=False,
                      default="user")  # serve per l identificazione user /admin / professor

    _courses = db.relationship("Course", secondary=user_course,
                               back_populates="_users")  # necessaria per relazione molti a molti !

    _school = db.Column(db.Integer, db.ForeignKey(
        'h_schools._hschool_id'))

    # uno a molti -> legata a chiave esterna professor
    _courses_prof = db.relationship('Course', backref='users', cascade="all, delete",
                                    passive_deletes=True)  # VALUTARE ON CASCADE DELETE

    def __repr__(self):
        return '<User %r>' % self.username

    def __init__(self, name, surname, email, password, role):
        self._name = name
        self._surname = surname
        self._email = email
        self._password = password
        self._role = role

    def get_id(self):
        return self._user_id
