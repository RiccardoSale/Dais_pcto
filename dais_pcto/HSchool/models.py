from dais_pcto.app import db
from flask_login import UserMixin


class Hschool(UserMixin, db.Model):
    __tablename__ = "h_schools"

    _id = db.Column(db.Integer, primary_key=True)
    _name = db.Column(db.String(64), nullable=False)
    _region = db.Column(db.String(20), nullable=False)
    _street = db.Column(db.String(64), nullable=False)
    _number = db.Column(db.String(3), nullable=False)
    _phone = db.Column(db.String(15),
                       nullable=False)  # Non vanno trattati come una sequenza numerica massimo 15 caratteri per numeri

    r_users = db.relationship('User', backref='h_schools')
