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

from .forms import EditProfile, EditProfileSeg
from ..Auth.models import User
from ..Auth.route import login, admin
from ..Courses.models import Course
from ..HSchool.models import Hschool
from ..Lessons.models import Lesson
from ..module_extensions import bcrypt

blueprint = Blueprint('BaseRoute', __name__)


@blueprint.route('/')
def index():
    return render_template('index.html')


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
        courses = Course.query.join(User._courses).join(Lesson).filter(User._user_id == current_user._user_id).all()

    form = EditProfile()
    if form.validate_on_submit():
        q = User.query.filter_by(_user_id=current_user._user_id).first()
        if check_password_hash(q._password, form.old_password.data):
            q.set_name(form.name.data)
            q.set_surname(form.surname.data)
            q.set_email(form.email.data)
            q.set_password(form.new_password.data)
            q.update()
            flash("Modifica avvenuta con successo!", "success")
            return redirect(
                url_for('BaseRoute.profile', form=form, courses=courses))  # redirect per resettare campi inseriti
        else:
            flash("Controlla la password inserita!", "danger")
    return render_template('profile.html', form=form, courses=courses)


@blueprint.route('/users', methods=("GET", "POST"))
@admin.require(http_exception=403)
@login_required
def users():
    form = EditProfileSeg()
    all_users = db.session.query(User).filter_by(_role="user").outerjoin(Hschool)
    if form.validate_on_submit():
        list = form.school.data.split(":")
        print(list)
        print("hello")
        db.session.query(Hschool).filter_by(_phone=list[-1]).first().add_student(  db.session.query(User).filter_by(_user_id=form.user.data).first() )
        flash("Scuola assegnata con successo")
    return render_template("users.html", users=all_users, form=form)
