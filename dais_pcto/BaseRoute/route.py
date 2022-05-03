from flask import Blueprint, render_template, flash, url_for, redirect
from flask_bcrypt import check_password_hash
from flask_login import login_required, current_user
from sqlalchemy.exc import InvalidRequestError, IntegrityError, DataError, InterfaceError, DatabaseError
from werkzeug.routing import BuildError

from dais_pcto.app import db

from .forms import EditProfile
from ..Auth.models import User
from ..Courses.models import Course
from ..module_extensions import bcrypt

blueprint = Blueprint('BaseRoute', __name__)


@blueprint.route('/')
def index():
    return render_template('index.html')


@blueprint.route('/profile', methods=("GET", "POST"))
@login_required
def profile():
    if current_user.role == "professor":
        courses = Course.query.filter_by(professor=current_user.id)
        print(courses)
    form = EditProfile()
    if form.validate_on_submit():
        try:
            q = User.query.filter_by(id=current_user.id).first()
            if check_password_hash(q.password, form.old_password.data):
                name = form.name.data  # da rifare con def per upload codice ripetuto = brutto
                if name != "":
                    q.name = name
                surname = form.surname.data
                if surname != "":
                    q.surname = surname
                username = form.username.data
                if username != "":
                    q.username = username
                email = form.email.data
                if email != "":
                    q.email = email
                new_psw = form.new_password.data
                if new_psw != "":
                    q.password = bcrypt.generate_password_hash(new_psw)
                db.session.commit()
                flash("Modifica avvenuta con successo!", "success")
                return redirect(
                    url_for('BaseRoute.profile', form=form, courses=courses))  # redirect per resettare campi inseriti
            else:
                flash("Invalid password!", "danger")

        except InvalidRequestError:
            db.session.rollback()
            flash(f"Something went wrong!", "danger")
        except IntegrityError:
            db.session.rollback()
            flash(f"User already exists!.", "warning")
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
    return render_template('profile.html', form=form, courses=courses)
