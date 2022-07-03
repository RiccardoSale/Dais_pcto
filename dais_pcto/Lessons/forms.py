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

# Dati richiesti per una singola lezione
class LessonsForm(FlaskForm):
    start_hour = TimeField(validators=[InputRequired()])
    end_hour = TimeField(validators=[InputRequired()])
    date = DateField('Date', format='%Y-%m-%d', validators=[InputRequired()])
    mode = SelectField('mode', choices=['presenza', 'online', 'blended'], validators=[InputRequired()])
    link = StringField(validators=[Optional()])
    structure = StringField(validators=[Optional()])
    description = StringField(validators=[InputRequired()])
    course = HiddenField(validators=[InputRequired()])
    submit1 = SubmitField('Aggiungi Lezione')

    # Controllo sull'ora di inizio
    def validate_start_hour(self, field):
        # L'ora di inizio della lezione non può essere dopo l'ora di fine della lezione
        if self.start_hour.data > self.end_hour.data:
            flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore!", 'warning')
            raise ValidationError("L'orario di inizio della lezione deve precedere l'orario di fine della lezione!")

        date_time_obj = datetime.strptime('09:00:00', '%H:%M:%S').time()
        # Le lezioni non possono cominciare prima delle 09:00
        if self.start_hour.data < date_time_obj:
            flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore!", 'warning')
            raise ValidationError("Le lezioni non possono iniziare prima delle 09:00!")

    # Controllo sull'ora di fine
    def validate_end_hour(self, field):
        # _course = corso a cui la lezione si riferisce
        _course = course_with_id(self.course.data).first()
        total_hour = _course._n_hour
        lessons = _course._lessons

        # La data della lezione deve essere compresa tra la data di inizio e di fine del corso
        if self.date.data < _course._start_date or self.date.data > _course._end_date:
            flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore!", 'warning')
            raise ValidationError("La data della lezione deve essere compresa nel periodo specifico del corso!")

        total_sum = timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0)
        # Per ogni lezione si sommano le ore
        for x in lessons:
            total_sum += datetime.combine(date.today(), x._end_hour) - datetime.combine(date.today(), x._start_hour)
        # Al totale delle ore si sommano le ore della lezione che si sta cercando di inserire
        total_sum += datetime.combine(date.today(), self.end_hour.data) - datetime.combine(date.today(), self.start_hour.data)
        total_sum_in_hours = total_sum.days * 24 + total_sum.seconds / 3600.0

        # Se il totale delle ore (compresa la lezione che si sta cercando di inserire) supera le ore dichiarate dal corso allora non è più possibile aggiungere lezioni
        if total_sum_in_hours > total_hour:
            flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore!", 'warning')
            raise ValidationError("Non si possono aggiungere lezioni oltre il numero totale delle ore specificate dal corso!")

        upper_limit = timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=6, weeks=0)
        lower_limit = timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=1, weeks=0)
        base = timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0)
        base += datetime.combine(date.today(), self.end_hour.data) - datetime.combine(date.today(), self.start_hour.data)

        # Una lezione può durare al massimo 6 ore
        if base > upper_limit:
            flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore", 'warning')
            raise ValidationError("La lezione non può durare più di 6 ore")

        # Una lezione può durare al minimo un'ora
        if base < lower_limit:
            flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore", 'warning')
            raise ValidationError("La lezione non può durare meno di 1 ora")

        # Per ogni lezione si controlla che la lezione che si sta inserendo non si accavalli con altre lezioni
        for x in lessons:
            if x._date == self.date.data:
                if (self.start_hour.data < x._end_hour < self.end_hour.data) or \
                        (x._start_hour < self.start_hour.data < x._end_hour) or \
                        (self.start_hour.data < x._start_hour and self.end_hour.data > x._end_hour) or \
                        (self.start_hour.data < x._start_hour < self.end_hour.data < x._end_hour):
                    flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore!", 'warning')
                    raise ValidationError(
                        "Esiste già una lezione di nome :" + x._description + " nella fascia oraria inserita!")

        # Le lezioni non possono terminare dopo le 20:00
        date_time_obj = datetime.strptime('20:00:00', '%H:%M:%S').time()
        if self.end_hour.data > date_time_obj:
            flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore!", 'warning')
            raise ValidationError("Le lezioni non possono terminare dopo le 20:00!")

    # Controllo della validità della data
    def validate_date(self, field):
        # La lezione che si vuole inserire deve essere dopo la data di oggi
        if str(self.date) <= str(datetime.now()):
            flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore!", 'warning')
            raise ValidationError("La data della lezione deve essere successiva a quella odierna!")

    # Controllo della modalità della lezione
    def validate_mode(self, field):
        # Recupero del corso associato alla lezione
        q = course_with_id(self.course.data).first()
        # Se la modalità del corso è 'presenza'
        if q._mode == "presenza":
            # Se la modalità della lezione è diversa da 'presenza' allora non c'è corrispondenza corso-lezione
            if field.data != "presenza":
                flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore!", 'warning')
                raise ValidationError("La modalità della lezione non combacia con quella del corso!")
            # Se è presente un link allora non c'è corrispondenza corso-lezione
            if self.link.data != "":
                flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore!", 'warning')
                raise ValidationError("Non si deve inserire il link se la modalità è in presenza!")
            # Se non è presente una struttura allora non c'è corrispondenza corso-lezione
            if self.structure.data == "":
                flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore!", 'warning')
                raise ValidationError("Necessario indicare una struttura se la lezione è in presenza!")
        # Se la modalità del corso è 'online'
        if q._mode == "online":
            # Se la modalità della lezione è diversa da 'online' allora non c'è corrispondenza corso-lezione
            if field.data != "online":
                flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore!", 'warning')
                raise ValidationError("La modalità della lezione non combacia con quella del corso!")
            # Se è non presente un link allora non c'è corrispondenza corso-lezione
            if self.link.data == "":
                flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore!", 'warning')
                raise ValidationError("Necessario inserire il link se la modalità è online!")
            # Se è presente una struttura allora non c'è corrispondenza corso-lezione
            if self.structure.data != "":
                flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore!", 'warning')
                raise ValidationError("Non si deve indicare una struttura se la lezione è online!")
        # Se la modalità del corso è 'blended'
        if q._mode == "blended":
            # Se non è presente un link allora non c'è corrispondenza corso-lezione
            if self.link.data == "":
                flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore!", 'warning')
                raise ValidationError("Poichè il corso è in modalità blended bisogna inserire il link!")
            # Se non è presente una struttura allora non c'è corrispondenza corso-lezione
            if self.structure.data == "":
                flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore!", 'warning')
                raise ValidationError("Poichè il corso è in modalità blended bisogna inserire una struttura!")

# Token segreto per registrare la presenza a una lezione
class TokenForm(FlaskForm):
    token = StringField(validators=[InputRequired(), Length(1, 32, message="Inserire un token valido")])
    id = HiddenField()
    user = HiddenField()
    submit_token = SubmitField("Registra la tua presenza")

    # Controllo sulla validità del token
    def validate_token(self, field):
        # Recupero della lezione associato al token
        l = lesson_with_id(self.id.data).first()
        # Recupero del corso associato alla lezione appena trovata (relativo all'utente)
        corso = db.session.query(User).join(Course._users).filter(User._user_id == self.user.data,
                                                                  Course._course_id == l.course).first()
        # Se non viene trovato un corso allora significa che l'utente non è iscritto a tale corso
        if not corso:
            raise ValidationError("Per registrare la presenza a una lezione è necessario iscriversi prima al corso!")

        # Verifica del token
        if self.token.data != l._secret_token:
            raise ValidationError("Il token inserito non risulta valido!")
        # Individuazione della lezione interessata se l'utente ha già dichiarato la presenza
        q = db.session.query(User).join(Lesson._users).filter(User._user_id == self.user.data,
                                                              Lesson._lesson_id == self.id.data).first()
        # Se q ha un risultato non si può dichiarare 2 volte la presenza di un lezione
        if q:
            raise ValidationError("La presenza a questa lezione è già stata registrata!")
        else:
            print("non trovato quindi registro la presenza")

# Rimozione di una lezione
class RemoveLesson(FlaskForm):
    id = HiddenField()
    user = HiddenField()
    password = PasswordField(validators=[InputRequired(), Length(8, 72)])
    submit_remove_lesson = SubmitField('Rimuovi Lezione')

    # Verificare che la password dell'utente coincida con l'utente che ha creato il corso che si desidera eliminare
    def validate_password(self, field):
        q = user_with_id(self.user.data).first()
        if not check_password_hash(q._password, field.data):
            flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore!", 'warning')
            raise ValidationError("Password non corretta!")

# Modifica di una lezione
class ModifyLesson(FlaskForm):
    start_hour = TimeField(validators=[Optional()])
    end_hour = TimeField(validators=[Optional()])
    date = DateField('Date', format='%Y-%m-%d', validators=[Optional()])
    mode = SelectField('mode', choices=['presenza', 'online', 'blended'], validators=[Optional()])
    link = StringField(validators=[Optional()])
    structure = StringField(validators=[Optional()])
    description = StringField(validators=[Optional()])
    lesson = HiddenField(validators=[InputRequired()])
    course = HiddenField(validators=[InputRequired()])
    submit_modify_lesson = SubmitField("Modifica Lezione")

    # Controllo della validità della data
    def validate_date(self, field):
        q = lesson_with_id(self.lesson.data).first()
        # Se la data inserita è prima della data odierna non è possibile la modifca
        if str(self.date) <= str(datetime.now()):
            flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore!", 'warning')
            raise ValidationError("La data della lezione deve essere successiva a quella odierna!")

        # Se la vecchia data è già passata allora non è possibile modificarla
        if q._date <= date.today():
            flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore!", 'warning')
            raise ValidationError("Non si possono modificare lezioni già avvenute!")

    # Controllo della validità della modalità
    def validate_mode(self, field):
        # Recupero del corso a cui la lezione si riferisce
        q = course_with_id(self.course.data).first()

        if field.data != "":
            # La modalità della lezione si può modificare solo se la modalità del corso a essa riferita è blended
            if q._mode != "blended":
                flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore!", 'warning')
                raise ValidationError("E' possibile modificare la modalità della lezione se e solo se la modalità del corso è blended")

    # Controllo della validità del link
    def validate_link(self, field):
        # Recupero della lezione associata
        q = lesson_with_id(self.lesson.data).first()

        if field.data != "":
            # Se la modalità è 'presenza' allora non ci deve essere un link
            if (self.mode.data == "presenza"):
                flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore!", 'warning')
                raise ValidationError("Se la lezione si tiene in presenza non ci può essere un link!")
        else:
            if self.mode.data == "presenza":
                field.data = "vuoto"

    # Controllo della validità della struttura
    def validate_structure(self, field):
        # Recupero della lezione associata
        q = lesson_with_id(self.lesson.data).first()

        if field.data != "":
            # Se la modalità è 'online' allor non ci deve essere una struttura
            if q._mode == "online" or self.mode.data == "online":
                flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore!", 'warning')
                raise ValidationError("Se la lezione si tiene online non ci può essere una struttura!")
        else:
            if self.mode.data == "online":
                field.data = "vuoto"

    # Controllo della validità dell'ora di inizio della lezione
    def validate_start_hour(self, field):
        if self.start_hour.data is not None:
            # Recupero della lezione associata
            q = lesson_with_id(self.lesson.data).first()
            # Ci sono due possibilità: l'ora di fine è stata modificata o l'ora di fine NON è stata mofidicata
            if self.end_hour.data is None:
                # Se l'ora di inizio è successiva all'ora di fine della lezione allora la modifica non è consentita
                if self.start_hour.data > self.end_hour.data:
                    flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore!", 'warning')
                    raise ValidationError("L'orario di inizio della lezione deve precedere l'orario di fine della lezione!")
            else:
                # Se l'ora di inizio è successiva all'ora di fine della lezione allora la modifica non è consentita
                if self.start_hour.data > q._end_hour:
                    flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore", 'warning')
                    raise ValidationError("# Se l'ora di inizio è successiva all'ora di fine della lezione allora la modifica non è consentita")


            date_time_obj = datetime.strptime('09:00:00', '%H:%M:%S').time()
            # Le lezioni non possono cominciare prima delle 09:00
            if self.start_hour.data < date_time_obj:
                flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore!", 'warning')
                raise ValidationError("Le lezioni non possono iniziare prima delle 09:00!")

    # Controllo validità dell'ora di fine della lezione
    def validate_end_hour(self, field):
        # Recupero della lezione associata
        q = lesson_with_id(self.lesson.data).first()
        # Recupero del corso associato alla lezione appena trovata
        _course = course_with_id(self.course.data).first()
        total_hour = _course._n_hour
        lessons = _course._lessons
        if self.end_hour.data is None:
            self.end_hour.data = q._end_hour
        if self.start_hour.data is None:
            self.start_hour.data = q._start_hour
        if self.date.data is None:
            self.date.data = q._date

        # Se la data inserita precede la data di inizio corso o è successiva alla data di fine corso, allora non è possibile la modifica
        if self.date.data < _course._start_date or self.date.data > _course._end_date:
            flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore!", 'warning')
            raise ValidationError("La data della lezione deve essere compresa nel periodo specifico del corso!")

        total_sum = timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0)
        # Per ogni lezione si sommano le ore
        for x in lessons:
            total_sum += datetime.combine(date.today(), x._end_hour) - datetime.combine(date.today(), x._start_hour)
        # Al totale delle ore si sommano le ore della lezione che si sta cercando di inserire
        total_sum += datetime.combine(date.today(), self.end_hour.data) - datetime.combine(date.today(), self.start_hour.data)
        total_sum_in_hours = total_sum.days * 24 + total_sum.seconds / 3600.0

        # Se il totale delle ore (compresa la lezione che si sta cercando di inserire) supera le ore dichiarate dal corso allora non è più possibile aggiungere lezioni
        if total_sum_in_hours > total_hour:
            flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore!", 'warning')
            raise ValidationError("Non si possono modificare gli orari delle lezioni se si supera il numero totale delle ore specificate dal corso!")

        # limit = limite massimo di durata di una lezione (6 ore)
        limit = timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=6, weeks=0)
        base = timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0)
        base += datetime.combine(date.today(), self.end_hour.data) - datetime.combine(date.today(), self.start_hour.data)

        # Se le ore della lezione superano le 6 ore non è possibile aggiungere la lezione
        if base > limit:
            flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore", 'warning')
            raise ValidationError("La lezione non può durare più di 6 ore!")

        # Per ogni lezione si controlla che la lezione che si sta inserendo non si accavalli con altre lezioni
        for x in lessons:
            if x._date == self.date.data:
                if (self.start_hour.data < x._end_hour < self.end_hour.data) or \
                        (x._start_hour < self.start_hour.data < x._end_hour) or \
                        (self.start_hour.data < x._start_hour and self.end_hour.data > x._end_hour) or \
                        (self.start_hour.data < x._start_hour < self.end_hour.data < x._end_hour):
                    flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore", 'warning')
                    raise ValidationError(
                        "Esiste già una lezione di nome :" + x._description + " nella fascia oraria inserita!")

        # Le lezioni non possono terminare dopo le 20:00
        date_time_obj = datetime.strptime('20:00:00', '%H:%M:%S').time()
        if self.end_hour.data > date_time_obj:
            flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore!", 'warning')
            raise ValidationError("Le lezioni non possono terminare dopo le 20:00!")
