from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, DateField, SubmitField, HiddenField
from wtforms.validators import InputRequired, Length, Regexp, ValidationError

from dais_pcto.Auth.models import User
from dais_pcto.Courses.models import Course
from dais_pcto.Lessons.models import Lesson
from dais_pcto.module_extensions import db


class coursesForm(FlaskForm):
    name = StringField(validators=[InputRequired(), Length(1, 64),
                                   Regexp("^[A-Za-z][A-Za-z0-9_.]*$", 0, "Il nome del corso non è valido")])
    mode = SelectField('mode', choices=['presenza', 'online', 'blended'])
    description = StringField(validators=[Regexp("^[A-Za-z][A-Za-z0-9]*$", 0, "Descrizione non valida")])
    max_student = IntegerField(validators=[InputRequired()])
    min_student = IntegerField(
        validators=[InputRequired()])  # DEVE ESSERE MINORE DI MAX STUDENT DOVE METTO VINCOLO
    n_hour = IntegerField(validators=[InputRequired()])
    start_month = DateField('Date', format='%Y-%m-%d', validators=[InputRequired()])
    end_month = DateField('Date', format='%Y-%m-%d', validators=[InputRequired()])

    def validate_end_month(self, field):
        if field.data < self.start_month.data:
            raise ValidationError("La data di fine del corso deve essere successiva alla data di inizio del corso")

    def validate_start_month(self, field):
        if str(field.data) < str(datetime.now()):
            raise ValidationError("Inserisci come data di inizio posteriore alla data odierna")

    def validate_max_student(self, field):
        if self.max_student.data < self.min_student.data:
            raise ValidationError("Il numero di studenti minimi deve essere minore del numero di studenti massimi")

    def validate_min_student(self, field):
        if field.data < 10:
            raise ValidationError("Il numero di studenti minimi deve essere almeno 10")


class CourseSubscription(FlaskForm):
    id = HiddenField()
    user = HiddenField()
    submit3 = SubmitField('Iscriviti al corso')

    def validate_id(self, data):
        q = db.session.query(User).join(Course._users).filter(User._user_id == self.user.data,
                                                              Course._course_id == self.id.data).first()
        if q:
            if q._role == "user":
                raise ValidationError("Sei già registrato al corso")
        else:
            q2 = db.session.query(Course).filter_by(_course_id=self.id.data).join(User).first()
            if len(q2._users) >= q2._max_student:
                raise ValidationError("Il corso è chiuso non sono più disponibili posti")


class PartecipationCertificate(FlaskForm):
    id = HiddenField()
    user = HiddenField()
    submit4 = SubmitField('Genera il certificato di Partecipazione')

    def validate_id(self, data):
        q = db.session.query(Lesson).join(Course).filter(Course._course_id == self.id.data).all()
        # q= LEZIONI CHE FANNO PARTE DEL CORSO ATTUALE DA CONFRONTARE CON LE LEZIONI SEGUITE DALLO STUDENTE DI QUEL CORSO PARTICOLARE

        #Lezioni a cui l utente ha partecipato di quel particolare corso e di cui ha registrato la presenza
        subquery = db.session.query(Lesson).join(User._lessons).filter(User._user_id==self.user.data,Lesson.course==self.id.data).all()

        #DEVE AVER PARTECIPATO ALMENO AL 70 %
        if len(subquery)/len(q)*100 < 70:
            raise ValidationError("Non hai attestato la partecipazione ad abbastanza lezioni")
