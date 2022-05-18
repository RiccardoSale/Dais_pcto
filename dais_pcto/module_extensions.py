from sqlite3 import IntegrityError

from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy, Model


class CRUDMixin(Model):
    """Mixin that adds convenience methods for CRUD (create, read, update, delete) operations."""

    def update(self):
        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise IntegrityError()

    def save(self, commit=True):
        """Save the record."""
        try:
            db.session.add(self)
            if commit:
                db.session.commit()
            return True
        except:
            db.session.rollback()
            raise IntegrityError()

    def delete(self):
        """Remove the record from the database."""
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except:
            db.session.rollback()
            raise IntegrityError()


bcrypt = Bcrypt()
db = SQLAlchemy(model_class=CRUDMixin)
migrate = Migrate()
