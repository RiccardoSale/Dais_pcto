from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, DateField, TimeField, HiddenField, SubmitField
from wtforms.validators import InputRequired, Length, Regexp, NumberRange, ValidationError
from dais_pcto.HSchool.models import Hschool
from dais_pcto.module_extensions import db


class SchoolForm(FlaskForm):
    code = StringField(validators=[Regexp(
            "^[A-Za-z]{4}[0-9]{6}$",message="Il codice meccanografico deve essere composto da 4 numeri seguiti da 6 caratteri"),InputRequired(), Length(10,10,
                                                           message="Il codice meccanografico della scuola deve essere composto da 10 caratteri")])
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
    # tipo -> liceo / professionale / tecnico
    submit1 = SubmitField('submit')  # per identificare i due form presenti nella stessa pagina

    # def validate_name(self, field):
    #     school = Hschool.query.filter_by(_name=field.data, _region=self.region.data, _city=self.city.data,
    #                                      _street=self.street.data, _number=self.number.data).first()

    def validate_code(self, field):
        school = db.session.query(Hschool).filter_by(_hschool_code=field.data).first()
        if school is not None:
            raise ValidationError("La scuola inserita è già presente")


class DeleteSchoolForm(FlaskForm):
    id = HiddenField()
    submit2 = SubmitField('submit')
