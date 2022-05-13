from datetime import datetime
from urllib import response

from flask import Blueprint, render_template, flash, url_for, redirect
from flask_bcrypt import check_password_hash
from flask_login import login_required, current_user
from sqlalchemy.exc import InvalidRequestError, IntegrityError, DataError, InterfaceError, DatabaseError
from werkzeug.routing import BuildError
from flask import render_template
from flask import make_response
import pdfkit
from dais_pcto.app import db

from .forms import EditProfile
from ..Auth.models import User
from ..Courses.models import Course
from ..Lessons.models import Lesson
from ..module_extensions import bcrypt

blueprint = Blueprint('BaseRoute', __name__)


@blueprint.route('/')
def index():
    return render_template('index.html')


@blueprint.route('/prova')
def prova():
    return render_template('prova.html')


def certificate(course, professor, ore):
    professor = db.session.query(User).filter_by(_user_id=professor).first()
    date = str(datetime.now())
    date = date[0:10]
    rendered = render_template('certificate.html', name=current_user._name, surname=current_user._surname,
                               professor=professor, course=course, date=date, ore=ore)
    path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
    pdf = pdfkit.from_string(rendered, False, configuration=config)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment;filename=output.pdf'
    return response


@blueprint.route('/profile', methods=("GET", "POST"))
@login_required
def profile():
    courses = ""
    if current_user._role == "professor":
        courses = Course.query.filter_by(_professor=current_user._user_id)

    if current_user._role == "user":
        courses = Course.query.join(User._courses).join(Lesson).filter(User._user_id==current_user._user_id).all()

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
                    q._password = bcrypt.generate_password_hash(new_psw).decode('utf8')
                db.session.commit()
                flash("Modifica avvenuta con successo!", "success")
                return redirect(url_for('BaseRoute.profile', form=form, courses=courses))  # redirect per resettare campi inseriti
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
