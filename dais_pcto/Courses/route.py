import secrets
from datetime import datetime, date, timedelta

from sqlalchemy import func, desc

from dais_pcto.Auth.route import admin, professor
from dais_pcto.Courses.models import *
from flask import Blueprint, url_for, current_app, redirect, g, flash, render_template
from flask_login import login_required, logout_user, login_user, current_user
from werkzeug.routing import BuildError
from sqlalchemy.exc import (IntegrityError, DataError, DatabaseError, InterfaceError, InvalidRequestError, )
from dais_pcto.app import db
from .forms import coursesForm, PartecipationCertificate, UnsubscribeCourse
from ..Auth.models import User, user_with_email, user_with_id
from dais_pcto import Lessons
from ..BaseRoute.route import certificate
from ..Courses.forms import CourseSubscription, RemoveCourse, ModifyCourse
from ..Lessons.forms import LessonsForm, TokenForm, RemoveLesson, ModifyLesson
from ..Lessons.models import Lesson, lesson_with_id

blueprint = Blueprint('courses', __name__, )


# Funzione per capire se si è raggiunto il numero massimo di studenti consentiti o no
def course_open_or_closed(count, max):
    if count < max:
        return "Corso aperto!"
    else:
        return "Corso chiuso!"


@blueprint.route('/courses')
def courses():
    # Individuazione di tutti i corsi
    all_course_prof = db.session.query(Course).join(User)
    return render_template('courses.html', courses=all_course_prof)


@blueprint.route('/<string:course>', methods=["GET", "POST"])
@login_required
def single_course(course):
    object_corse = courses_with_name(course).first()
    # Possibili form utilizzabili su un singolo corso
    lesson_form = LessonsForm()
    token_form = TokenForm()
    course_subscription_form = CourseSubscription()
    certificate_form = PartecipationCertificate()
    remove_course_form = RemoveCourse()
    remove_lesson_form = RemoveLesson()
    modify_course_form = ModifyCourse()
    modify_lesson_form = ModifyLesson()
    unsubscribe_course_form = UnsubscribeCourse()
    info_corso = courses_with_name(course).join(User).first_or_404()
    # Utente iscritto al corso interessato
    utente_iscritto = db.session.query(Course).join(User._courses).filter(User._user_id == current_user._user_id,
                                                                          Course._name == course).first()
    owner_of_course = False
    if object_corse._professor == current_user._user_id:
        owner_of_course = True

    # Se l'utente non è presente allora significa che non è iscritto
    if utente_iscritto is None:
        utente_iscritto = "noniscritto"

    # course_lesson = lezioni che sono associate al corso interessato in ordine di data e di ora
    course_lesson = db.session.query(Lesson).join(Course).filter(Course._name == course).order_by(
        Lesson._date).order_by(Lesson._start_hour)
    # count = numero lezioni totali
    count = len(info_corso._users)
    progress_bar = 0
    # attivo = capire se il corso ha ancora posti disponibili
    attivo = course_open_or_closed(count, info_corso._max_student)

    numero_ore_fatte = timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0)
    zero = timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0)

    # Per ogni lezioni del corso
    for x in course_lesson:
        # Se la data della lezione precede o è uguale a quella di oggi, il numero di ore fatte incrementa
        if x._date <= date.today():
            numero_ore_fatte += datetime.combine(date.today(), x._end_hour) - datetime.combine(date.today(),
                                                                                               x._start_hour)

    # Se il numero di ore supera 0 allora la barra di progresso del corso sarà proprozionale al numero di ore di lezione sostenute
    if numero_ore_fatte > zero:
        progress_bar = int(((numero_ore_fatte.seconds / 3600) / info_corso._n_hour) * 100)

    # Aggiunta di una lezione
    if lesson_form.submit1.data and lesson_form.validate_on_submit():
        Lesson(lesson_form.start_hour.data, lesson_form.end_hour.data, lesson_form.date.data, lesson_form.mode.data,
               lesson_form.link.data,
               lesson_form.structure.data, lesson_form.description.data, info_corso._course_id,
               secrets.token_hex(16)).save()
        flash("La lezione è stata aggiunta con successo!", "success")
        return redirect(url_for('courses.single_course', course=course))

    # Dichiarazione della presenza a una determinata lezione
    if token_form.submit_token.data and token_form.validate_on_submit():
        l = lesson_with_id(token_form.id.data).first()
        current_user.subscribe_lesson(l)
        flash("La presenza è stata registrata con successo!", "success")

    # Iscrizione a un corso
    if course_subscription_form.submit_subcription_course.data and course_subscription_form.validate_on_submit():
        current_user.subscribe_course(object_corse)
        flash("L'iscrizione è avvenuta con successo!", "success")
        return redirect(url_for('courses.single_course', course=course))

    # Generazione del certificato di partecipazione
    if certificate_form.submit_certificate.data and certificate_form.validate_on_submit():
        return certificate(course=info_corso._name, professor=info_corso._professor, ore=info_corso._n_hour)

    # Rimozione di un corso
    if remove_course_form.submit_remove_course.data and remove_course_form.validate_on_submit():
        object_corse.delete()
        all_course_prof = db.session.query(Course).join(User)
        return render_template('courses.html', courses=all_course_prof)

    # Rimozione di una lezione
    if remove_lesson_form.submit_remove_lesson.data and remove_lesson_form.validate_on_submit():
        q = lesson_with_id(remove_lesson_form.id.data).first()
        q.delete()
        flash("lezione rimossa con successo", "success")
        return redirect(url_for('courses.single_course', course=course))

    # Modifica di un corso
    if modify_course_form.submit_modify_course.data and modify_course_form.validate_on_submit():
        object_corse.set_name(modify_course_form.name.data)

        # Se c'è il professore associato questo rimane uguale anche dopo la modifica
        if modify_course_form.professor.data is not None:
            prof = user_with_email(modify_course_form.professor.data).first()
            prof.professor_course(object_corse)

        object_corse.set_description(modify_course_form.description.data)
        object_corse.set_max_student(modify_course_form.max_student.data)
        object_corse.set_n_hour(modify_course_form.n_hour.data)
        object_corse.set_start_date(modify_course_form.start_date.data)
        object_corse.set_end_date(modify_course_form.end_date.data)
        object_corse.update()
        flash("I dati del corso sono stati aggiornati con successo!", "success")
        return redirect(url_for('courses.single_course', course=modify_course_form.name.data))

    # Modifica di una lezione
    if modify_lesson_form.submit_modify_lesson.data and modify_lesson_form.validate_on_submit():
        q = lesson_with_id(modify_lesson_form.lesson.data).first()
        q.set_start_hour(modify_lesson_form.start_hour.data)
        q.set_end_hour(modify_lesson_form.end_hour.data)
        q.set_mode(modify_lesson_form.mode.data)
        q.set_link(modify_lesson_form.link.data)
        q.set_structure(modify_lesson_form.structure.data)
        q.set_description(modify_lesson_form.description.data)
        q.update()
        flash("La lezione è stata aggiornata con successo!", "success")

    # Disiscrizione da un corso
    if unsubscribe_course_form.submit_unsub_course.data and unsubscribe_course_form.validate_on_submit():  # disiscrivo l utente
        q = user_with_id(unsubscribe_course_form.user.data).first()
        q.unsubscribe_course(object_corse)
        flash("La disiscrizione dal corso è stata effettuata correttamente!", "success")
        return redirect(url_for('courses.single_course', course=object_corse._name))

    return render_template('single_course.html', Course=info_corso, attivo=attivo, progress_bar=progress_bar,
                           Lessons=course_lesson, lesson_form=lesson_form, token_form=token_form,
                           course_subscription_form=course_subscription_form, certificate_form=certificate_form,
                           remove_course_form=remove_course_form, remove_lesson_form=remove_lesson_form,
                           modify_course_form=modify_course_form, modify_lesson_form=modify_lesson_form,
                           utente_iscritto=utente_iscritto,
                           unsubscribe_course_form=unsubscribe_course_form,
                           owner_of_course=owner_of_course)


@blueprint.route('/buildcourse', methods=("GET", "POST"))
@professor.require(http_exception=403)  # la creazione del coros richiede di essere almeno professor
@login_required
# Creazione di un corso
def buildcourse():
    # Recupero dei dati necessari
    form = coursesForm()
    if form.validate_on_submit():
        # Inserimento del professore relativo al corso creato
        if form.professor.data is not None:
            professor = user_with_email(form.professor.data).first()
        else:
            professor = current_user

        Course(form.name.data, form.mode.data, form.description.data, form.max_student.data,
               form.min_student.data, form.n_hour.data, form.start_date.data, form.end_date.data,
               professor._user_id).save()

        flash("Il corso è stato creato con successo!", "success")
        return redirect(url_for('courses.single_course', course=form.name.data))

    return render_template('buildcourse.html', name=current_user._user_id, form=form, title="Course",
                           btn_action="Create course")
