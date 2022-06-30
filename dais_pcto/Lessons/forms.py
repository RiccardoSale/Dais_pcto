from datetime import datetime, time, timedelta, date
from flask import flash
from flask_bcrypt import check_password_hash
from flask_wtf import FlaskForm
from markupsafe import Markup
from wtforms import StringField, SelectField, IntegerField, DateField, TimeField, HiddenField, SubmitField, \
    PasswordField
from wtforms.validators import InputRequired, Length, Regexp, ValidationError, Optional

from dais_pcto.Courses.models import Course, course_with_id
from dais_pcto.Lessons.models import *
from dais_pcto.Auth.models import User, user_with_id
from dais_pcto.module_extensions import db


# start hour deve essere prima di end hour
# date deve essere compresa tra il periodo del corso
# date non puo essere precedente alla data di oggi perche se stiamo creando un corso non puo essere nel passato

# le lezioni dello stesso giorno dello stesso corso non si sovrappongono
# l'orario delle lezioni e compreso tra le 9 e le 20


# SE una lezione è online il campo struttura va lasciato vuoto
# se la lezione blended o in presenza il campo struttura va indicato e popolato


# SE una lezione è online il campo link è obbligatorio #fatto!
# Se una lezione e blendend campo link  obbligatorio!!!
# Se una lezione e in presenza campo link non obbligatorio !!!!


# Se il corso è in presenza le lezioni devono essere in presenza
# Se il corso è online non abbiamo lezioni in presenza


# LEZIONE DEVE DURARE AL MASSIMO 6 ORE


class LessonsForm(FlaskForm):
    start_hour = TimeField(validators=[InputRequired()])
    end_hour = TimeField(validators=[InputRequired()])
    date = DateField('Date', format='%Y-%m-%d', validators=[InputRequired()])
    mode = SelectField('mode', choices=['presenza', 'online', 'blended'], validators=[InputRequired()])
    link = StringField(validators=[Optional()])
    structure = StringField(validators=[Optional()])  # Possibile campo choices
    description = StringField(validators=[InputRequired()])
    course = HiddenField(validators=[InputRequired()])
    submit1 = SubmitField('Aggiungi Lezione')

    def validate_start_hour(self, field):
        if self.start_hour.data > self.end_hour.data:
            flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore", 'warning')
            raise ValidationError("L'orario di fine lezione deve essere successivo all'orario di inizio lezione")

        date_time_obj = datetime.strptime('09:00:00', '%H:%M:%S').time()
        if self.start_hour.data < date_time_obj:
            flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore", 'warning')
            raise ValidationError("L'orario di inizio deve essere maggiore delle 09:00")

    def validate_end_hour(self, field):
        ####VALIDAZIONE NON POSSO SFORARE ORE TOTALI####
        _course = course_with_id(self.course.data).first()
        total_hour = _course._n_hour
        lessons = _course._lessons

        if self.date.data < _course._start_date or self.date.data > _course._end_date:
            flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore", 'warning')
            raise ValidationError("La data della lezione deve essere compresa nel periodo del corso")

        total_sum = timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0)
        for x in lessons:
            total_sum += datetime.combine(date.today(), x._end_hour) - datetime.combine(date.today(), x._start_hour)

        total_sum += datetime.combine(date.today(), self.end_hour.data) - datetime.combine(date.today(),
                                                                                           self.start_hour.data)
        total_sum_in_hours = total_sum.days * 24 + total_sum.seconds / 3600.0  # per questo

        if total_sum_in_hours > total_hour:
            flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore", 'warning')
            raise ValidationError("Non puoi più aggiungere lezioni oltre il numero totale delle ore corso")

        upper_limit = timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=6, weeks=0)
        lower_limit = timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=6, weeks=0)
        base = timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0)
        base += datetime.combine(date.today(), self.end_hour.data) - datetime.combine(date.today(),
                                                                                      self.start_hour.data)

        if base > upper_limit:
            flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore", 'warning')
            raise ValidationError("La lezione non può durare più di 6 ore")

        if base < lower_limit:
            flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore", 'warning')
            raise ValidationError("La lezione non può durare meno di 1 ora")

        for x in lessons:
            if x._date == self.date.data:
                if (self.start_hour.data < x._end_hour < self.end_hour.data) or \
                        (x._start_hour < self.start_hour.data < x._end_hour) or \
                        (self.start_hour.data < x._start_hour and self.end_hour.data > x._end_hour) or \
                        (self.start_hour.data < x._start_hour < self.end_hour.data < x._end_hour):
                    flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore", 'warning')
                    raise ValidationError(
                        "Lezione già esistente di nome :" + x._description + " nella fascia oraria inserita")

        date_time_obj = datetime.strptime('20:00:00', '%H:%M:%S').time()
        if self.end_hour.data > date_time_obj:
            flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore", 'warning')
            raise ValidationError("L'orario di fine deve essere prima delle 20:00")

    def validate_date(self, field):
        if str(self.date) <= str(datetime.now()):
            flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore", 'warning')
            raise ValidationError("La data della lezione deve essere successiva a quella odierna")

    def validate_mode(self, field):
        q = course_with_id(self.course.data).first()
        if q._mode == "presenza":
            if field.data != "presenza":
                flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore", 'warning')
                raise ValidationError("La modalità della lezione non combacia con quella del corso")
            if self.link.data != "":
                flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore", 'warning')
                raise ValidationError("Non bisogna inserire il link se la modalità è in presenza")
            if self.structure.data == "":
                flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore", 'warning')
                raise ValidationError("Bisogna indicare una struttura se la lezione è in presenza")
        if q._mode == "online":
            if field.data != "online":
                flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore", 'warning')
                raise ValidationError("La modalità della lezione non combacia con quella del corso")
            if self.link.data == "":
                flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore", 'warning')
                raise ValidationError("Bisogna inserire il link se la modalità è online")
            if self.structure.data != "":
                flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore", 'warning')
                raise ValidationError("Non puoi indicare una struttura se la lezione è online")
        if q._mode == "blended":
            if self.link.data == "":
                flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore", 'warning')
                raise ValidationError("Poichè il corso è in modalità blended bisogna inserire il link")
            if self.structure.data == "":
                flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore", 'warning')
                raise ValidationError("Poichè il corso è in modalità blended bisogna indicare una struttura")


class TokenForm(FlaskForm):
    token = StringField(validators=[InputRequired(), Length(1, 32, message="Please provide a valid token")])
    id = HiddenField()
    user = HiddenField()
    submit_token = SubmitField("Registra la tua presenza")

    def validate_token(self, field):
        l = lesson_with_id(self.id.data).first()
        corso = db.session.query(User).join(Course._users).filter(User._user_id == self.user.data,
                                                                  Course._course_id == l.course).first()
        if not corso:
            raise ValidationError("Per registrare la presenza a una lezione iscriviti prima al corso")

        if self.token.data != l._secret_token:
            raise ValidationError("token inserito non valido")
        q = db.session.query(User).join(Lesson._users).filter(User._user_id == self.user.data,
                                                              Lesson._lesson_id == self.id.data).first()
        if q:
            raise ValidationError("Sei già registrato a questa lezione")
        else:
            print("non trovato quindi registro la presenza")


class RemoveLesson(FlaskForm):
    id = HiddenField()
    user = HiddenField()
    password = PasswordField(validators=[InputRequired(), Length(8, 72)])
    submit_remove_lesson = SubmitField('Rimuovi Lezione')

    def validate_password(self, field):
        q = user_with_id(self.user.data).first()
        if not check_password_hash(q._password, field.data):
            flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore", 'warning')
            raise ValidationError("Password non corretta")

# COSA LASCIAMO MODIFICARE E COME DI UNA LEZIONE
# modalita la lasciamo cambiare sole se il corso e blended
# la farei modificare solo se non già avvenuta
# possibile modificare tutti i campi
class ModifyLesson(FlaskForm):
    start_hour = TimeField(validators=[Optional()])
    end_hour = TimeField(validators=[Optional()])
    date = DateField('Date', format='%Y-%m-%d', validators=[Optional()])
    mode = SelectField('mode', choices=['presenza', 'online', 'blended'], validators=[Optional()]) #compare solo se il corso è blended
    link = StringField(validators=[Optional()])
    structure = StringField(validators=[Optional()])
    description = StringField(validators=[Optional()])
    lesson = HiddenField(validators=[InputRequired()])
    course = HiddenField(validators=[InputRequired()])
    submit_modify_lesson = SubmitField("Modifica Lezione")

    def validate_date(self, field):
        q = lesson_with_id(self.lesson.data).first()
        if str(self.date) <= str(datetime.now()):
            flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore", 'warning')
            raise ValidationError("La data della lezione deve essere successiva a quella odierna")

        if q._date <= date.today():  # vedere se aggiungere a template
            flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore", 'warning')
            raise ValidationError("Non puoi modificare lezioni che sono già avvenute / completate")

    def validate_mode(self, field):
        q = course_with_id(self.course.data).first()

        if field.data != "":
            if q._mode != "blended":
                flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore", 'warning')
                raise ValidationError(
                    "E' possibile modificare la modalità della lezione se e solo se la modalità del corso è blended")

    def validate_link(self, field):
        q = lesson_with_id(self.lesson.data).first()

        if field.data != "":
            if (self.mode.data == "presenza"):
                flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore", 'warning')
                raise ValidationError("Se la modalità è in presenza non ci può essere un link")
        else:
            if self.mode.data == "presenza":
                field.data = "vuoto"

    def validate_structure(self, field):
        q = lesson_with_id(self.lesson.data).first()

        if field.data != "":
            if q._mode == "online" or self.mode.data == "online":
                flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore", 'warning')
                raise ValidationError("Se la modalità è online non ci può essere una struttura")
        else:
            if self.mode.data == "online":
                field.data = "vuoto"

    def validate_start_hour(self, field):
        if self.start_hour.data is not None:
            q = lesson_with_id(self.lesson.data).first()
            if self.end_hour.data is None:
                if self.start_hour.data > self.end_hour.data:
                    flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore", 'warning')
                    raise ValidationError(
                        "L'orario di fine lezione deve essere successivo all'orario di inizio lezione")
            else:
                if self.start_hour.data > q._end_hour:
                    flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore", 'warning')
                    raise ValidationError(
                        "L'orario di fine lezione deve essere successivo all'orario di inizio lezione")

            date_time_obj = datetime.strptime('09:00:00', '%H:%M:%S').time()
            if self.start_hour.data < date_time_obj:
                flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore", 'warning')
                raise ValidationError("L'orario di inizio deve essere maggiore delle 09:00")

    def validate_end_hour(self, field):
        ####VALIDAZIONE NON POSSO SFORARE ORE TOTALI####
        q = lesson_with_id(self.lesson.data).first()
        _course = course_with_id(self.course.data).first()
        total_hour = _course._n_hour
        lessons = _course._lessons
        if self.end_hour.data is None:
            self.end_hour.data = q._end_hour
        if self.start_hour.data is None:
            self.start_hour.data = q._start_hour
        if self.date.data is None:
            self.date.data = q._date

        if self.date.data < _course._start_date or self.date.data > _course._end_date:
            flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore", 'warning')
            raise ValidationError("La data della lezione deve essere compresa nel periodo del corso")

        total_sum = timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0)
        for x in lessons:
            total_sum += datetime.combine(date.today(), x._end_hour) - datetime.combine(date.today(), x._start_hour)

        total_sum += datetime.combine(date.today(), self.end_hour.data) - datetime.combine(date.today(),
                                                                                           self.start_hour.data)
        total_sum_in_hours = total_sum.days * 24 + total_sum.seconds / 3600.0  # per questo

        if total_sum_in_hours > total_hour:
            flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore", 'warning')
            raise ValidationError("Non puoi più aggiungere lezioni oltre il numero totale delle ore corso")

        limit = timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=6, weeks=0)
        base = timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0)
        base += datetime.combine(date.today(), self.end_hour.data) - datetime.combine(date.today(),
                                                                                      self.start_hour.data)

        if base > limit:
            flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore", 'warning')
            raise ValidationError("La lezione non può durare più di 6 ore")

        for x in lessons:
            if x._date == self.date.data:
                if (self.start_hour.data < x._end_hour < self.end_hour.data) or \
                        (x._start_hour < self.start_hour.data < x._end_hour) or \
                        (self.start_hour.data < x._start_hour and self.end_hour.data > x._end_hour) or \
                        (self.start_hour.data < x._start_hour < self.end_hour.data < x._end_hour):
                    flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore", 'warning')
                    raise ValidationError(
                        "Lezione già esistente di nome :" + x._description + " nella fascia oraria inserita")

        date_time_obj = datetime.strptime('20:00:00', '%H:%M:%S').time()
        if self.end_hour.data > date_time_obj:
            flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore", 'warning')
            raise ValidationError("L'orario di fine deve essere prima delle 20:00")
