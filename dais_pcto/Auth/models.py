from flask_login import UserMixin
from dais_pcto.app import db

user_course = db.Table('user_corse',
                       db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
                       db.Column('course_id', db.Integer, db.ForeignKey('courses.id'))
                       )


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    name = db.Column(db.String(64), unique=False, nullable=False)
    surname = db.Column(db.String(64), unique=False, nullable=False)
    email = db.Column(db.String(60), unique=True, nullable=False, index=True)
    password = db.Column(db.String(128),
                         nullable=False)  # lunghezza dopo hashing CONTROLLARE DOPO AVER LIMITATO PASSWORD A TOT CARATTERI

    # relazioni
    # molti a molti
    # relazione con la scuola di appartenenza e

    # pensa all entita scuola aggiunge la relazione
    # è fatta identica alla relazione dei corsi

    # cambiare form iscrizione aggiungendo campo choice -> con scuole

    r_courses = db.relationship("Course", secondary=user_course, back_populates="r_users")

    r_school = db.Column(db.Integer, db.ForeignKey(
        'schools._id'))

    # uno a molti
    r_courses_prof = db.relationship('Course', backref='users', cascade="all, delete",
                                     passive_deletes=True)  # VALUTARE ON CASCADE DELETE

    role = db.Column(db.String(10), nullable=False,
                     default="user")  # serve per l identificazione user /admin / professor

    def __repr__(self):
        return '<User %r>' % self.username
