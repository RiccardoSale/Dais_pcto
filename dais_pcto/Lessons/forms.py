from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, DateField, TimeField
from wtforms.validators import InputRequired, Length, Regexp


class LessonsForm(FlaskForm):
    start_hour = TimeField(validators=[InputRequired()])
    end_hour = TimeField(validators=[InputRequired()])
    date = DateField('Date', format='%Y-%m-%d', validators=[InputRequired()])
    mode = SelectField('mode', choices=['presenza', 'online', 'blended'], validators=[InputRequired()])
    link = StringField(validators=[InputRequired()])
    structure = StringField(validators=[Length(1, 64, message="Indica una struttura di riferimento dell ateno")]) #Possibile campo choices
    description = StringField(validators=[InputRequired()])
