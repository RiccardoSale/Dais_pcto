from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, DateField
from wtforms.validators import InputRequired, Length, Regexp, ValidationError


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
