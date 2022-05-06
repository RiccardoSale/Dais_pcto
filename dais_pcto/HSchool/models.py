from sqlalchemy import UniqueConstraint

from dais_pcto.app import db
from flask_login import UserMixin


class Hschool(UserMixin, db.Model):
    __tablename__ = "h_schools"
    __table_args__ = (UniqueConstraint("_name", "_region", "_city", "_street", "_number"),)
    # AGGIUNGERE CHECK !
    _hschool_id = db.Column(db.Integer, primary_key=True)
    _name = db.Column(db.String(64), nullable=False)
    _region = db.Column(db.String(20), nullable=False)
    _city = db.Column(db.String(40), nullable=False)
    _street = db.Column(db.String(64), nullable=False)
    _number = db.Column(db.String(3), nullable=False)
    _phone = db.Column(db.String(15),
                       nullable=False)  # Non vanno trattati come una sequenza numerica massimo 15 caratteri per numeri

    r_users = db.relationship('User', backref='h_schools')

    # Costruttore oggetto
    def __init__(self, name, region, city, street, number, phone):
        self._name = name
        self._region = region
        self._city = city
        self._street = street
        self._number = number
        self._phone = phone
