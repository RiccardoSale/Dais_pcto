from datetime import datetime

from flask import flash
from flask_bcrypt import check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, DateField, SubmitField, HiddenField, PasswordField
from wtforms.validators import InputRequired, Length, Regexp, ValidationError, Optional

from dais_pcto.Auth.models import User
from dais_pcto.Courses.models import Course
from dais_pcto.Lessons.models import Lesson
from dais_pcto.module_extensions import db


def all_professor():
    return db.session.query(User).filter_by(_role="professor")


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

    professor = SelectField(validators=[Optional()], choices=all_professor)

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


class CourseSubscription(FlaskForm):  # decidere se far iscrivere anche dopo la data di inizio
    id = HiddenField()
    user = HiddenField()
    submit_subcription_course = SubmitField('Iscriviti al corso')

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
    submit_certificate = SubmitField('Genera il certificato di Partecipazione')

    def validate_id(self, data):
        q = db.session.query(Lesson).join(Course).filter(Course._course_id == self.id.data).all()
        # q= LEZIONI CHE FANNO PARTE DEL CORSO ATTUALE DA CONFRONTARE CON LE LEZIONI SEGUITE DALLO STUDENTE DI QUEL CORSO PARTICOLARE

        # Lezioni a cui l utente ha partecipato di quel particolare corso e di cui ha registrato la presenza
        subquery = db.session.query(Lesson).join(User._lessons).filter(User._user_id == self.user.data,
                                                                       Lesson.course == self.id.data).all()

        # DEVE AVER PARTECIPATO ALMENO AL 70 %
        if len(subquery) / len(q) * 100 < 70:
            raise ValidationError("Non hai attestato la partecipazione ad abbastanza lezioni")


class RemoveCourse(FlaskForm):  # Eliminarle anche se ci sono lezioni
    user = HiddenField()
    password = PasswordField(validators=[InputRequired(), Length(8, 72)])
    submit_remove_course = SubmitField('Rimuovi corso')

    def validate_password(self, field):
        q = db.session.query(User).filter_by(_user_id=self.user.data).first()
        if not check_password_hash(q._password, field.data):
            raise ValidationError("Password non corretta")


class UnsubscribeCourse(FlaskForm):
    user = HiddenField(validators=[InputRequired()])
    submit_unsub_course = SubmitField('Disiscriviti')


class ModifyCourse(FlaskForm):
    name = StringField(validators=[Length(1, 64),
                                   Regexp("^[A-Za-z][A-Za-z0-9_.]*$", 0, "Il nome del corso non è valido"), Optional()])
    professor = SelectField(validators=[Optional()], choices=all_professor)
    description = StringField(validators=[Regexp("^[A-Za-z][A-Za-z0-9]*$", 0, "Descrizione non valida"), Optional()])
    max_student = IntegerField(validators=[Optional()])
    n_hour = IntegerField(validators=[Optional()])
    start_month = DateField('Date', format='%Y-%m-%d', validators=[Optional()])
    end_month = DateField('Date', format='%Y-%m-%d', validators=[Optional()])
    course_id = HiddenField(validators=[InputRequired()])
    submit_modify_course = SubmitField('Modifica corso')

    def validate_end_month(self, field):
        if self.start_month.data is not None:
            if field.data < self.start_month.data:
                flash("Controlla il form qualcosa è andato storto")
                raise ValidationError("La data di fine del corso deve essere successiva alla data di inizio del corso")
        else:
            if field.data is not None:
                q = db.session.query(Course).filter_by(_course_id=self.course_id.data).first()
                if field.data < q._start_month:
                    raise ValidationError(
                        "La data di fine del corso deve essere successiva alla data di inizio del corso")

                lessons = db.session.query(Lesson).join(Course).filter(
                    Course._course_id == self.course_id.data).order_by(
                    Lesson._date).all()
                if lessons[-1]._date > self.end_month.data:
                    ValidationError("Ci sono delle lezioni prima della data di fine corso si sta cercando di inserire")

    def validate_start_month(self, field):
        if field.data is not None:
            if str(field.data) < str(datetime.now()):
                raise ValidationError("Inserisci come data di inizio posteriore alla data odierna")

            lessons = db.session.query(Lesson).join(Course).filter(Course._course_id == self.course_id.data).order_by(
                Lesson._date).all()
            if lessons[0]._date < self.start_month.data:
                ValidationError("Ci sono delle lezioni prima della data di inizio corso che stai cercando di inserire")

    def validate_max_student(self, field):
        if field.data is not None:
            print("bagigio")
            print(field.data)
            q = db.session.query(Course).filter_by(_course_id=self.course_id.data).first()
            if field.data < q._max_student:
                flash("Controlla il form qualcosa è andato storto")
                raise ValidationError("Puoi solo aumentare i posti disponibili")

    def validate_n_hour(self, field):
        if field.data is not None:
            q = db.session.query(Course).filter_by(_course_id=self.course_id.data).first()
            if q._n_hour > field.data:
                raise ValidationError("Puoi solo aumentare le ore di lezione")
