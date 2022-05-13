from datetime import datetime, time, timedelta, date

from flask_wtf import FlaskForm
from markupsafe import Markup
from wtforms import StringField, SelectField, IntegerField, DateField, TimeField, HiddenField, SubmitField
from wtforms.validators import InputRequired, Length, Regexp, ValidationError

from dais_pcto.Courses.models import Course
from dais_pcto.Lessons.models import Lesson
from dais_pcto.Auth.models import User
from dais_pcto.module_extensions import db


# start hour deve essere prima di end hour
# date deve essere compresa tra il periodo del corso
# date non puo essere precedente alla data di oggi perche se stiamo creando un corso non puo essere nel passato

# le lezioni dello stesso giorno dello stesso corso non si sovrappongono
# l'orario delle lezioni e compreso tra le 9 e le 20


# SE una lezione è online il campo struttura va lasciato vuoto
# se la lezione blended o in presenza il campo struttura va indicato e popolato


class LessonsForm(FlaskForm):
    start_hour = TimeField(validators=[InputRequired()])
    end_hour = TimeField(validators=[InputRequired()])
    date = DateField('Date', format='%Y-%m-%d', validators=[InputRequired()])
    mode = SelectField('mode', choices=['presenza', 'online', 'blended'], validators=[InputRequired()])
    link = StringField(validators=[InputRequired()])
    structure = StringField()  # Possibile campo choices
    description = StringField(validators=[InputRequired()])
    course = HiddenField(validators=[InputRequired()])
    submit1 = SubmitField('submit')

    ## Le lezioni di un corso non si devono sovrappore ! -> TODO

    # NON far aggiungere una lezione che va a sforare le ore del corso totali ->TODO

    def validate_start_hour(self, field):
        if self.start_hour.data > self.end_hour.data:
            raise ValidationError("L'orario di fine lezione deve essere successivo all'orario di inizio lezione")

        date_time_obj = datetime.strptime('09:00:00', '%H:%M:%S').time()
        if self.start_hour.data < date_time_obj:
            raise ValidationError("L'orario di inizio deve essere maggiore delle 09:00")

    def validate_end_hour(self, field):
        ####VALIDAZIONE NON POSSO SFORARE ORE TOTALI####
        _course = db.session.query(Course).filter_by(_name=self.course.data).first()
        total_hour = _course._n_hour
        lessons = _course._lessons

        if self.date.data < _course._start_month or self.date.data > _course._end_month:
            raise ValidationError("La data della lezione deve essere compresa nel periodo del corso")

        total_sum = timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0)
        for x in lessons:
            total_sum += datetime.combine(date.today(), x._end_hour) - datetime.combine(date.today(), x._start_hour)

        total_sum += datetime.combine(date.today(), self.end_hour.data) - datetime.combine(date.today(),
                                                                                           self.start_hour.data)
        total_sum_in_hours = total_sum.days * 24 + total_sum.seconds / 3600.0  # per questo

        if total_sum_in_hours > total_hour:
            raise ValidationError("Non puoi più aggiungere lezioni oltre il numero totale delle ore corso")
        #####FINE VALIDAZIONE####

        for x in lessons:
            if x._date == self.date.data:
                if (self.start_hour.data < x._end_hour < self.end_hour.data) or \
                        (x._start_hour < self.start_hour.data < x._end_hour) or \
                        (self.start_hour.data < x._start_hour and self.end_hour.data > x._end_hour) or \
                        (self.start_hour.data < x._start_hour < self.end_hour.data < x._end_hour):
                    raise ValidationError(
                        "Lezione già esistente di nome :" + x._description + " nella fascia oraria inserita")

                #  #   se 1 inizia prima di della fine di 2 e la fine di 1 e dopo
                #  if  self.start_hour.data < x._end_hour and self.end_hour.data > x._end_hour:
                #
                # #se 1 inizia durante 2 e finisce durante 2
                # if self.start_hour.data < x._end_hour and self.end_hour.data < x._end_hour:
                #
                #
                # # se 1 inizia prima di 2 e finisce dopo 2
                # if self.start_hour.data < x._start_hour and self.end_hour.data > x._end_hour:
                #
                # #se 1 inizia prima di 2 e finisce durante 2
                # if self.start_hour.data < x._start_hour and self.end_hour.data < x._end_hour:

        date_time_obj = datetime.strptime('20:00:00', '%H:%M:%S').time()
        if self.end_hour.data > date_time_obj:
            raise ValidationError("L'orario di fine deve essere prima delle 20:00")

    # def validate_description(self, field):

    def validate_date(self, field):
        if str(self.date) <= str(datetime.now()):
            raise ValidationError("La data della lezione deve essere successiva a quella odierna")

    def validate_mode(self, field):
        if field.data == "online":
            if self.structure.data != "":
                raise ValidationError("Se la lezione è online non va indicata la struttura")
        else:
            if self.structure.data == "":
                raise ValidationError(
                    "Indica una struttura di riferimento! La lezione è in modalità  " + self.mode.data)


class TokenForm(FlaskForm):
    token = StringField(validators=[InputRequired(), Length(1, 32, message="Please provide a valid token")])
    id = HiddenField()
    user = HiddenField()
    submit2 = SubmitField("Registra la tua presenza")

    def validate_token(self, field):
        l = db.session.query(Lesson).filter_by(_lesson_id=self.id.data).first()
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
