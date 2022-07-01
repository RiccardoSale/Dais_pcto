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
from ..Auth.models import User, user_with_id, users_with_role
from ..Auth.route import login, admin
from ..Courses.models import Course, courses_with_professor
from ..HSchool.models import Hschool, school_with_phone
from ..Lessons.models import Lesson
from ..module_extensions import bcrypt

blueprint = Blueprint('BaseRoute', __name__)

@blueprint.route('/')
# Funzione per rimandare alla pagina iniziale
def index():
    return render_template('index.html')

# Funzione per il certificato del corso
def certificate(course, professor, ore):
    professor = user_with_id(professor).first()
    date = str(datetime.now())
    date = date[0:10]
    # Rimando alla pagina in cui è presente il certificato per l'utente
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
# Funzione per identificare l'utente
def profile():
    courses = ""
    list = []
    # Se l'utente ha ruolo 'professor', la variabile 'courses' contiene i corsi che l'utente insegna
    if current_user._role == "professor":
        print("professor")
        courses = courses_with_professor(current_user._user_id)
    # Se l'utente ha ruolo 'user', la variabile 'courses' contiene i corsi a cui l'utente si è iscritto
    if current_user._role == "user":
        courses = db.session.query(Course).join(User._courses).filter(User._user_id == current_user._user_id)
        # Si individuano tutte le lezioni dei corsi a cui l'utente vuole partecipare
        for c in courses:
            list.append(db.session.query(Lesson).join(User._lessons).filter(User._user_id == current_user._user_id,
                                                                            Lesson.course == c._course_id).all())

    # Modifica del profilo
    form = EditProfile()
    # Se i dati inseriti sono validi
    if form.validate_on_submit():
        # Si ricava l'utente dai dati inseriti
        q = user_with_id(current_user._user_id).first()
        # Il controllo per la modifica parte dall'inserimento della password corretta
        if check_password_hash(q._password, form.old_password.data):
            q.set_name(form.name.data)
            q.set_surname(form.surname.data)
            q.set_email(form.email.data)
            q.set_password(form.new_password.data)
            q.update()
            flash("La modifica è avvenuta con successo!", "success")
            # La redirect è necessaria per resettare i campi appena inseriti
            return redirect(
                url_for('BaseRoute.profile', form=form, courses=courses,
                        list=list))
        else:
            # Se la password non è corretta si avvisa l'utente
            flash("Controlla la password inserita!", "danger")

    return render_template('profile.html', form=form, courses=courses, list=list)


@blueprint.route('/users', methods=("GET", "POST"))
@admin.require(http_exception=403)
@login_required
# Funzione per assegnare a un utente con suolo 'user' la scuola di provenienza
def users():
    form = EditProfileSeg()
    all_users = users_with_role("user").outerjoin(Hschool)
    # Se i dati inseriti sono validi
    if form.validate_on_submit():
        q = user_with_id(form.user.data).first()
        q.set_name(form.name.data)
        q.set_surname(form.surname.data)
        q.update()
        list = form.school.data.split(":")
        # Si associa l'utente alla scuola dichiarata
        school_with_phone(list[-1]).first().add_student(q)
        flash("La scuola è assegnata con successo!", "success")
    return render_template("users.html", users=all_users, form=form)
