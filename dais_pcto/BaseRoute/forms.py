from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, HiddenField
from wtforms.validators import Length, Regexp, Email, InputRequired, Optional

from dais_pcto.HSchool.models import all_schools
from dais_pcto.module_extensions import db


# Per la modifica del profilo è necessario inserire la email, la nuova password, la vecchia password, il nome e il cognome
class EditProfile(FlaskForm):
    email = StringField(validators=[Email(), Length(1, 64), Optional()])
    new_password = PasswordField(validators=[Length(8, 72), Optional()])
    old_password = PasswordField(
        validators=[InputRequired(message="La password che si vuol modificare è necessaria per il cambio credenziali"), Length(8, 72)])
    # Il nome e il cognome devono contenere caratteri consoni (non possono esserci numeri o caratteri particolari)
    name = StringField(validators=[Length(3, 64, message="Inserire un nome valido"), Optional(), Regexp(
        "^[A-Za-z][A-Za-z_.àèìòù, ]*$", 0, "Il nome deve contenere caratteri consoni",)])
    surname = StringField(
        validators=[Length(3, 20, message="Inserire un cognome valido"), Optional(), Regexp(
            "^[A-Za-z][A-Za-z_.àèìòù, ]*$", 0, "Il cognome deve contenere caratteri consoni",)])

# I dati richiesti per associare un utente alla scuola di provenienza sono
# il nome, il cognome, l'id dell'utente e la scuola
class EditProfileSeg(FlaskForm):
    # Il nome e il cognome devono contenere caratteri consoni (non possono esserci numeri o caratteri particolari)
    name = StringField(validators=[Length(3, 64, message="Inserire un nome valido"), Optional(), Regexp(
        "^[A-Za-z][A-Za-z_.àèìòù, ]*$", 0, "Il nome deve contenere caratteri consoni",)])
    surname = StringField(
        validators=[Length(3, 20, message="Inserire un cognome valido"), Optional(), Regexp(
            "^[A-Za-z][A-Za-z_.àèìòù, ]*$", 0, "Il cognome deve contenere caratteri consoni", )])
    school = SelectField(validators=[Optional()], choices=all_schools)
    user = HiddenField(validators=[Optional()])

