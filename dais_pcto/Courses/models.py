from dais_pcto.app import db
from flask_login import UserMixin
from dais_pcto.Auth.models import user_course


class Course(UserMixin, db.Model):
    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False, index=True)
    mode = db.Column(db.Integer, nullable=False)  # modalita 0 = online modalità 1 = presenza modalita 3 = blendend
    description = db.Column(db.TEXT, nullable=False, default="Descrizione non ancora disponibile")
    max_student = db.Column(db.Integer, nullable=False)
    min_student = db.Column(db.Integer, nullable=False)
    n_hour = db.Column(db.Integer, nullable=False)
    start_month = db.Column(db.DATE, nullable=False)  # da start month o end month ricavo periodo
    end_month = db.Column(db.DATE, nullable=False)

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
