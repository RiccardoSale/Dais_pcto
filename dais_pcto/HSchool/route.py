from flask import Blueprint, flash, redirect, url_for, render_template, request
from werkzeug.routing import BuildError

from dais_pcto.app import db
from .forms import SchoolForm, DeleteSchoolForm
from .models import Hschool
from sqlalchemy.exc import (IntegrityError, DataError, DatabaseError, InterfaceError, InvalidRequestError, )

blueprint = Blueprint('Hschool', __name__)


@blueprint.route('/schools', methods=("GET", "POST"))
def schools():
    form = SchoolForm()
    if form.submit1.data and form.validate_on_submit():
        try:
            new_school = Hschool(form.name.data, form.region.data, form.city.data, form.street.data, form.number.data,
                                 form.phone.data)
            db.session.add(new_school)
            db.session.commit()
            flash(f"Scuola inserita!", "success")
            print("prova")
            return redirect(url_for('Hschools.schools'))  # cambiare indirizzo di render

        except InvalidRequestError:
            db.session.rollback()
            flash(f"Something went wrong!", "danger")
        except IntegrityError:
            db.session.rollback()
            flash(f"An error has occurred!.", "warning")
        except DataError:
            db.session.rollback()
            flash(f"Invalid Entry", "warning")
        except InterfaceError:
            db.session.rollback()
            flash(f"Error connecting to the database", "danger")
        except DatabaseError:
            db.session.rollback()
            flash(f"Error connecting to the database", "danger")
        except BuildError:
            db.session.rollback()
            flash(f"An error occured !", "danger")
    q = db.session.query(Hschool)
    form2 = DeleteSchoolForm()
    if form2.submit2.data and form2.validate_on_submit():
        print("ziobagigio")
        rhschool = db.session.query(Hschool).filter_by(_hschool_id=form2.id.data).first()
        db.session.delete(rhschool)
        db.session.commit()
        print(form2.id.data)
    # DOBBIAMO PRENDERE IL DATO IN QUALCHE MODO DALLA DEF ->

    return render_template('schools.html', form=form, form2=form2, schools=q)
