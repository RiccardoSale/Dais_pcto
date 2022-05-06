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


@blueprint.route('/prova')
def prova():
    return render_template('prova.html')


@blueprint.route('/profile', methods=("GET", "POST"))
@login_required
def profile():
    subscribed_users = []
    courses = ""
    if current_user._role == "professor":
        # return count of user "id" grouped
        # by "name"
        # session.query(func.count(User.id)). \ ->utile per pagina corso singolo ??
        #     group_by(User.name)
        courses = Course.query.filter_by(_professor=current_user._user_id)
        for elem in courses:  # passo i campi che mi servono
            subscribed_users.append(len(elem._users))  # meglio usare query o usare len ???
    if current_user._role == "user":
        courses = User.query.filter_by(_user_id=current_user._user_id).first()
        courses = courses._courses

    form = EditProfile()
    if form.validate_on_submit():
        try:
            q = User.query.filter_by(_user_id=current_user._user_id).first()
            if check_password_hash(q._password, form.old_password.data):
                name = form.name.data  # da rifare con def per upload codice ripetuto = brutto
                if name != "":
                    q._name = name
                surname = form.surname.data
                if surname != "":
                    q._surname = surname
                email = form.email.data
                if email != "":
                    q._email = email
                new_psw = form.new_password.data
                if new_psw != "":
                    q._password = bcrypt.generate_password_hash(new_psw)
                db.session.commit()
                flash("Modifica avvenuta con successo!", "success")
                return redirect(
                    url_for('BaseRoute.profile', form=form, courses=courses,
                            subscribed_users=subscribed_users))  # redirect per resettare campi inseriti
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
    return render_template('profile.html', form=form, courses=courses, subscribed_users=subscribed_users)
