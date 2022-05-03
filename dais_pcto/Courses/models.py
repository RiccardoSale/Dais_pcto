from sqlalchemy import CheckConstraint

from dais_pcto.app import db
from flask_login import UserMixin
from dais_pcto.Auth.models import user_course


class Course(UserMixin, db.Model):
    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False, index=True)
    mode = db.Column(db.Integer, nullable=False)  # modalita 0 = online modalità 1 = presenza modalita 3 = blendend
    description = db.Column(db.TEXT, nullable=False, default="Descrizione non ancora disponibile")
    max_student = db.Column(db.Integer, CheckConstraint('max_student > min_student', name='max_stud_costr'),
                            nullable=False)
    min_student = db.Column(db.Integer, CheckConstraint('min_student < max_student', name='min_stud_costr'),
                            nullable=False)



    n_hour = db.Column(db.Integer, nullable=False)#DIVENTA RICAVATO

    start_month = db.Column(db.DATE, CheckConstraint('str(end_month) > str(start_month)', name='start_month_costr'),
                            nullable=False)
    end_month = db.Column(db.DATE, CheckConstraint('str(start_month) < str(end_month)', name='end_month_costr'),
                          nullable=False)# da start month o end month ricavo periodo



    #NUMERO LEZIONI STABILITO A PRIORI -> PROGRAMMA SETTIMANA -> 2 LEZIONI NORMALI DA 1 ORA E MEZZA -> 1 LEZIONE SPECIALE DA 3 ORE


    # relazioni
    #molti a molti
    lessons = db.relationship('Lesson', backref='courses')

    professor = db.Column(db.Integer, db.ForeignKey(
        'users.id',
        ondelete="CASCADE"))  # ->chiave esterna a utente -> e poi vincolo trigger blocca inserimento e la modifica di un eventuale utente che non abbia ruolo professore
    # email professore la piglio dall'utente ->

    r_users = db.relationship("User", secondary=user_course, back_populates="r_courses")

    def __repr__(self):
        return '<Course %r>' % self.name
