from sqlalchemy import UniqueConstraint

from dais_pcto.app import db
from flask_login import UserMixin


class Hschool(UserMixin, db.Model):
    __tablename__ = "h_schools"

    _hschool_code = db.Column(db.String(10), primary_key=True)
    _name = db.Column(db.String(64), nullable=False)
    _region = db.Column(db.String(20), nullable=False)
    _city = db.Column(db.String(40), nullable=False)
    _street = db.Column(db.String(64), nullable=False)
    _number = db.Column(db.String(6), nullable=False)
    _phone = db.Column(db.String(15),
                       nullable=False)  # Non vanno trattati come una sequenza numerica massimo 15 caratteri per numeri

    r_users = db.relationship('User', backref='h_schools')

    def __repr__(self):
        return "Nome: " + self._name + " Regione:  " + self._region + " Telefono:" + self._phone

    # Costruttore oggetto
    def __init__(self, code, name, region, city, street, number, phone):
        self._hschool_code = code
        self._name = name
        self._region = region
        self._city = city
        self._street = street
        self._number = number
        self._phone = phone

    def add_student(self, user):
        if user:
            self.r_users.append(user)
            self.update()

def school_with_code(code):
    return db.session.query(Hschool).filter_by(_hschool_code=code)

def all_schools():
    return db.session.query(Hschool)

def school_with_phone(phone):
    return db.session.query(Hschool).filter_by(_phone=phone)