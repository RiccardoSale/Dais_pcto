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

def user_with_id(id):
    return db.session.query(User).filter_by(_user_id=id)

def courses_with_professor(professor):
    return db.session.query(Course).filter_by(_professor=professor)

def users_with_role(role):
    return db.session.query(User).filter_by(_role=role)

def school_with_phone(phone):
    return db.session.query(Hschool).filter_by(_phone=phone)

@blueprint.route('/')
def index():
    return render_template('index.html')


def certificate(course, professor, ore):
    professor = user_with_id(professor).first()
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
    list = []
    if current_user._role == "professor":
        print("professor")
        courses = courses_with_professor(current_user._user_id)
    if current_user._role == "user":
        courses = db.session.query(Course).join(User._courses).filter(User._user_id == current_user._user_id)
        for c in courses:
            list.append(db.session.query(Lesson).join(User._lessons).filter(User._user_id == current_user._user_id,
                                                                            Lesson.course == c._course_id).all())

    form = EditProfile()
    if form.validate_on_submit():
        q = user_with_id(current_user._user_id).first()
        if check_password_hash(q._password, form.old_password.data):
            q.set_name(form.name.data)
            q.set_surname(form.surname.data)
            q.set_email(form.email.data)
            q.set_password(form.new_password.data)
            q.update()
            flash("Modifica avvenuta con successo!", "success")
            return redirect(
                url_for('BaseRoute.profile', form=form, courses=courses,
                        list=list))  # redirect per resettare campi inseriti
        else:
            flash("Controlla la password inserita!", "danger")
    return render_template('profile.html', form=form, courses=courses, list=list)


@blueprint.route('/users', methods=("GET", "POST"))
@admin.require(http_exception=403)
@login_required
def users():
    form = EditProfileSeg()
    all_users = users_with_role("user").outerjoin(Hschool)
    if form.validate_on_submit():
        list = form.school.data.split(":")
        school_with_phone(list[-1]).first().add_student(
            user_with_id(form.user.data).first())
        flash("Scuola assegnata con successo", "success")
    return render_template("users.html", users=all_users, form=form)
