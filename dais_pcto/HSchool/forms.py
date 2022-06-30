from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, DateField, TimeField, HiddenField, SubmitField
from wtforms.validators import InputRequired, Length, Regexp, NumberRange, ValidationError
from dais_pcto.HSchool.models import school_with_code
from dais_pcto.module_extensions import db

# Per la scuola è necessario l'inserimento di diversi dati
class SchoolForm(FlaskForm):
    code = StringField(validators=[Regexp("^[A-Z]{4}[0-9]{6}$", message="Il codice meccanografico della scuola deve essere composto da 4 lettere seguiti da 6 numeri"), InputRequired(),
                                   Length(10, 10, message="Il codice meccanografico della scuola deve essere composto da 10 caratteri")])
    name = StringField(validators=[InputRequired(), Length(3, 64, message="Inserire un nome valido!")])
    region = SelectField('mode', choices=['Abruzzo', 'Basilicata', 'Calabria', 'Campania', 'Emilia-Romagna',
                                          'FriuliVeneziaGiulia', 'Lazio', 'Liguria', 'Lombardia', 'Marche', 'Molise',
                                          'Piemonte', 'Puglia', 'Sardegna', 'Sicilia', 'Toscana', 'Trentino-Alto Adige',
                                          'Umbria', 'Valle d\' Aosta', 'Veneto'], validators=[InputRequired()])
    city = StringField(validators=[InputRequired(), Length(3, 40, message="Inserire una città valida!")])
    street = StringField(validators=[InputRequired(), Length(3, 64, message="Inserire un indirizzo valido!")])
    number = StringField(validators=[InputRequired(), Length(1, 5, message="Inserire un numero civico valido!")])
    phone = StringField(validators=[InputRequired(), Length(9, 10, message="Inserire un numero di telefono valido!")])
    # Necessario per identificare i due form presenti nella stessa pagina
    submit1 = SubmitField('Invia')

    # Verificare che la scuola non sia già stata inserita
    def validate_code(self, field):
        school = school_with_code(field.data).first()
        if school is not None:
            raise ValidationError("La scuola inserita è già presente!")

# Rimozione di una scuola
class DeleteSchoolForm(FlaskForm):
    id = HiddenField()
    submit2 = SubmitField('Elimina')
