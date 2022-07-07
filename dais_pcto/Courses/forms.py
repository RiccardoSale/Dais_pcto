from datetime import datetime, date

from flask import flash
from flask_bcrypt import check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, DateField, SubmitField, HiddenField, PasswordField
from wtforms.validators import InputRequired, Length, Regexp, ValidationError, Optional

from dais_pcto.Auth.models import User, user_with_id, users_with_role
from dais_pcto.Courses.models import *
from dais_pcto.Lessons.models import Lesson
from dais_pcto.module_extensions import db


# Funzione per individuare tutti gli utenti con il ruolo 'professor'
def all_professor():
    return users_with_role("professor")

# Per inserire un corso sono necessarie diverse informazioni
class coursesForm(FlaskForm):
    name = StringField(validators=[InputRequired(), Length(1, 64), Regexp("^[A-Za-z][A-Za-z0-9_.'àèìòù, ]*$", 0, "Il nome del corso deve contenere caratteri consoni")])
    mode = SelectField('mode', choices=['presenza', 'online', 'blended'])
    description = StringField(validators=[Regexp("^[A-Za-z][A-Za-z0-9'àèìòù.,:;!?() ]*$", 0, "La descrizione del corso deve contenere caratteri consoni")])
    max_student = IntegerField(validators=[InputRequired()])
    min_student = IntegerField(validators=[InputRequired()])
    n_hour = IntegerField(validators=[InputRequired()])
    start_date = DateField('Date', format='%Y-%m-%d', validators=[InputRequired()])
    end_date = DateField('Date', format='%Y-%m-%d', validators=[InputRequired()])
    # Indica il professore associato
    professor = SelectField(validators=[Optional()], choices=all_professor)

    # Funzione per controllare che la data di fine corso sia valida
    def validate_end_date(self, field):
        if field.data < self.start_date.data:
            raise ValidationError("La data di fine del corso deve essere successiva alla data di inizio del corso!")

    # Funzione per controllare che la data di inizio corso sia valida
    def validate_start_date(self, field):
        if str(field.data) < str(datetime.now()):
            raise ValidationError("La data di inizio corso deve essere una data posteriore alla data odierna!")

    # Funzione per controllare che il massimo numero di studenti sia effettivamente maggiore del numero minimo dichiarato
    def validate_max_student(self, field):
        if self.max_student.data < self.min_student.data:
            raise ValidationError("Il numero di studenti minimi deve essere minore del numero di studenti massimi consentiti!")

    # Il numero minimo di studenti per un corso è 10
    def validate_min_student(self, field):
        if field.data < 10:
            raise ValidationError("Il numero di studenti minimi deve essere almeno 10!")

# Dati richiesti per l'iscrizione a un corso da parte di un utente con ruolo 'user'
class CourseSubscription(FlaskForm):
    id = HiddenField()
    user = HiddenField()
    submit_subcription_course = SubmitField('Iscriviti al corso!')

    # Controllo per verificare che l'utente non sia già iscritto
    def validate_id(self, data):
        # q = id dell'utente che vuole iscriversi al corso, se si è già iscritto al medesimo
        q = db.session.query(User).join(Course._users).filter(User._user_id == self.user.data,
                                                              Course._course_id == self.id.data).first()
        # Se il risultato non è vuoto si fa un controllo
        if q:
            # Se l'utente è già iscritto non è possibile farlo ri-iscrivere
            if q._role == "user":
                raise ValidationError("Sei già registrato al corso!")
        else:
            q2 = course_with_id(self.id.data).join(User).first()
            # Se si è raggiunto il numero massimo di posti non è possibile iscirversi
            if len(q2._users) >= q2._max_student:
                raise ValidationError("Il corso ha raggiunto il numero massimo di posti disponibili!")

# Generazione del certificato di partecipazione
class PartecipationCertificate(FlaskForm):
    id = HiddenField()
    user = HiddenField()
    submit_certificate = SubmitField('Genera il certificato di Partecipazione')

    # Controllo sulla validità dell'utente
    def validate_id(self, data):
        # q = Lezioni che sono associate al corso interessato
        q = db.session.query(Lesson).join(Course).filter(Course._course_id == self.id.data).all()

        # subquery = Lezioni a cui l'utente ha partecipato di quel determinato corso
        # e di cui ha registrato la presenza
        subquery = db.session.query(Lesson).join(User._lessons).filter(User._user_id == self.user.data,
                                                                       Lesson.course == self.id.data).all()

        # Si è deciso che il certificato viene generato solo se l'utente ha partecipato ad almeno il 70 % delle lezioni
        # Se sono presenti lezioni
        if len(q) > 0:
            # Controllo per verificare che il corso sia terminato
            if str(course_with_id(self.id.data).first()._end_date) >= str(datetime.now()):
                raise ValidationError("Il corso non è ancora finito!")
            else:
                # Per generare il certificato è necessario che l'utente abbia registrato almeno il 70% delle presenze
                if len(subquery) / len(q) * 100 < 70:
                    raise ValidationError("Non è stata attestata la partecipazione ad almeno il 70% delle lezioni!")
        else:
            flash("Non ci sono lezioni!")

# Rimozione di un corso
# è possibile eliminare un corso anche se ci sono lezioni non ancora tenute
class RemoveCourse(FlaskForm):
    user = HiddenField()
    password = PasswordField(validators=[InputRequired(), Length(8, 72)])
    submit_remove_course = SubmitField('Rimuovi corso')

    # Controllo sulla password dell'utente
    def validate_password(self, field):
        q = user_with_id(self.user.data).first()
        if not check_password_hash(q._password, field.data):
            flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore!", 'warning')
            raise ValidationError("Password non corretta!")

# Disiscrizione dal corso
class UnsubscribeCourse(FlaskForm):
    user = HiddenField(validators=[InputRequired()])
    submit_unsub_course = SubmitField('Disiscriviti')

# Dati richiesti per la modifica del corso
class ModifyCourse(FlaskForm):
    name = StringField(validators=[Length(1, 64), Regexp("^[A-Za-z][A-Za-z0-9_.'àèìòù, ]*$", 0, "Il nome del corso deve contenere caratteri consoni"), Optional()])
    professor = SelectField(validators=[Optional()], choices=all_professor)
    description = StringField(validators=[Regexp("^[A-Za-z][A-Za-z0-9'àèìòù.,:;!?() ]*$", 0, "La descrizione del corso deve contenere caratteri consoni"), Optional()])
    max_student = IntegerField(validators=[Optional()])
    n_hour = IntegerField(validators=[Optional()])
    start_date = DateField('Date', format='%Y-%m-%d', validators=[Optional()])
    end_date = DateField('Date', format='%Y-%m-%d', validators=[Optional()])
    course_id = HiddenField(validators=[InputRequired()])
    submit_modify_course = SubmitField('Modifica corso')

    # Controllo sulla validità della data di fine corso
    def validate_end_date(self, field):
        # Possibili due casi: la data di inizio corso viene cambiata o la data di inizio corso NON viene cambiata
        if self.start_date.data is not None:
            # Verificare che la data di fine corso sia successiva alla data di inizio corso
            if field.data < self.start_date.data:
                flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore!", 'warning')
                raise ValidationError("La data di fine del corso deve essere successiva alla data di inizio del corso!")
        else:
            if field.data is not None:
                q = course_with_id(self.course_id.data).first()
                # Verificare che la data di fine corso sia successiva alla data di inizio corso
                if field.data < q._start_date:
                    flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore!", 'warning')
                    raise ValidationError("La data di fine del corso deve essere successiva alla data di inizio del corso!")

                # lessons = Lezioni che si riferiscono al corso interessato
                lessons = db.session.query(Lesson).join(Course).filter(
                    Course._course_id == self.course_id.data).order_by(
                    Lesson._date).all()
                # Se c'è una lezione dopo della nuova data di fine corso inserita allora la modifica non è concessa
                if lessons[-1]._date > self.end_date.data:
                    flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore!", 'warning')
                    raise ValidationError("Ci sono delle lezioni dopo della data di fine corso che si sta cercando di inserire!")

    # Controllo sulla validità della data di inizio corso
    def validate_start_date(self, field):
        if field.data is not None:
            # Verificare che la data di inizio corso sia successiva alla data odierna
            if str(field.data) < str(datetime.now()):
                flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore!", 'warning')
                raise ValidationError("La data di inizio del corso deve essere successiva alla data odierna!")

            # lessons = Lezioni che si riferiscono al corso interessato
            lessons = db.session.query(Lesson).join(Course).filter(Course._course_id == self.course_id.data).order_by(
                Lesson._date).all()
            # Se c'è una lezione prima della nuova data di inizio corso inserita allora la modifica non è concessa
            if lessons and lessons[0]._date < self.start_date.data:
                flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore!", 'warning')
                ValidationError("Ci sono delle lezioni prima della data di inizio corso che si sta cercando di inserire!")

    # Controllo sul numero massimo di studenti ammessi
    def validate_max_student(self, field):
        if field.data is not None:
            q = course_with_id(self.course_id.data).first()
            # Se il nuovo numero massimo è minore del vecchio numero massimo, la modifica non è consentita
            if field.data < q._max_student:
                flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore!", 'warning')
                raise ValidationError("I posti disponibili si possono solo aumentare!")

    # Controllo sul numero di ore del corso
    def validate_n_hour(self, field):
        if field.data is not None:
            q = course_with_id(self.course_id.data).first()
            # Se il nuovo numero di ore è minore del vecchio numero di ore, la modifica non è consentita
            if q._n_hour > field.data:
                flash("Operazione non riuscita. Riaprire il form per visualizzare l'errore!", 'warning')
                raise ValidationError("Le ore totali del corso si possono solo aumentare!")
