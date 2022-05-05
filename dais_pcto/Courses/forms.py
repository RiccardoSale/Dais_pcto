from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, DateField
from wtforms.validators import InputRequired, Length, Regexp


class coursesForm(FlaskForm):
    name = StringField(validators=[InputRequired(), Length(1, 64),
                                   Regexp("^[A-Za-z][A-Za-z0-9_.]*$", 0, "Il nome del corso non è valido")])
    mode = SelectField('mode', choices=['presenza', 'online', 'blended'])
    description = StringField(validators=[Regexp("^[A-Za-z][A-Za-z0-9]*$", 0, "Descrizione non valida")])
    max_student = IntegerField(validators=[InputRequired()])
    min_student = IntegerField(validators=[InputRequired()])  # DEVE ESSERE MINORE DI MAX STUDENT DOVE METTO VINCOLO
    n_hour = IntegerField(validators=[InputRequired()])
    start_month = DateField('Date', format='%Y-%m-%d', validators=[InputRequired()])
    end_month = DateField('Date', format='%Y-%m-%d', validators=[InputRequired()])
