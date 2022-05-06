from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, DateField, TimeField
from wtforms.validators import InputRequired, Length, Regexp, NumberRange, ValidationError
from dais_pcto.HSchool.models import Hschool


class SchoolForm(FlaskForm):
    name = StringField(validators=[InputRequired(), Length(3, 64, message="Indica un nome valido ")])
    region = SelectField('mode', choices=['Abruzzo', 'Basilicata', 'Calabria', 'Campania', 'Emilia-Romagna',
                                          'FriuliVeneziaGiulia', 'Lazio', 'Liguria', 'Lombardia', 'Marche', 'Molise',
                                          'Piemonte', 'Puglia', 'Sardegna', 'Sicilia', 'Toscana', 'Trentino-Alto Adige',
                                          'Umbria', 'Valle d\' Aosta', 'Veneto'], validators=[InputRequired()])
    city = StringField(validators=[InputRequired(), Length(3, 40,
                                                           message="Indica una città valida ")])  # eventuale lista per regione trovare dati
    street = StringField(validators=[InputRequired(), Length(3, 64, message="Indica un indirizzo corretto ")])
    number = StringField(validators=[InputRequired(), Length(1, 5, message="Civico non valido")])
    phone = StringField(validators=[InputRequired(), Length(9, 10, message="Indica un numero di telefono valido")])

    def validate_name(self, field):
        school = Hschool.query.filter_by(_name=field.data, _region=self.region.data, _city=self.city.data,
                                         _street=self.street.data, _number=self.number.data).first()
        if school is not None:
            raise ValidationError("La scuola inserita è già presente")


class DeleteSchoolForm(FlaskForm):
    id = IntegerField()
