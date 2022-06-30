from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, DateField, PasswordField
from wtforms.validators import InputRequired, Length, Regexp, Email, ValidationError, Optional
from .models import user_with_email

# Per il login viene richiesta una email e una password
class LoginForm(FlaskForm):
    email = StringField(validators=[InputRequired(), Email(), Length(1, 64)])
    password = PasswordField(validators=[Optional()])

# Per iscriversi è necessario inserire una email, una password, un nome e un cognome
class SignupForm(FlaskForm):
    email = StringField(validators=[InputRequired(), Email(), Length(1, 64)])
    password = PasswordField(validators=[InputRequired(), Length(8, 72)])
    # Il nome e il cognome devono contenere caratteri consoni (non possono esserci numeri o caratteri particolari)
    name = StringField(validators=[InputRequired(), Length(3, 64, message="Inserire un nome valido"), Regexp(
        "^[A-Za-z][A-Za-z_. ]*$", 0, "Il nome deve contenere caratteri consoni", )])
    surname = StringField(
        validators=[InputRequired(), Length(3, 20, message="Inserire un cognome valido"), Regexp(
            "^[A-Za-z][A-Za-z_. ]*$", 0, "Il cognome deve contenere caratteri consoni", )])

    # Controllo sulla email (la email inserita nell'iscrizione non deve già esistere)
    def validate_email(self, field):
        if user_with_email(field.data).first():
            raise ValidationError("Email già registrata!")



