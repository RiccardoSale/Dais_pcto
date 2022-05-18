import secrets
from datetime import datetime, date, timedelta

from sqlalchemy import func, desc

from dais_pcto.Auth.route import admin, professor
from dais_pcto.Courses.models import Course
from flask import Blueprint, url_for, current_app, redirect, g, flash, render_template
from flask_login import login_required, logout_user, login_user, current_user
from werkzeug.routing import BuildError
from sqlalchemy.exc import (IntegrityError, DataError, DatabaseError, InterfaceError, InvalidRequestError, )
from dais_pcto.app import db
from .forms import coursesForm, PartecipationCertificate
from ..Auth.models import User
from dais_pcto import Lessons
from ..BaseRoute.route import certificate
from ..Courses.forms import CourseSubscription, RemoveCourse, ModifyCourse
from ..Lessons.forms import LessonsForm, TokenForm, RemoveLesson, ModifyLesson
from ..Lessons.models import Lesson

blueprint = Blueprint('courses', __name__, )


def course_open_or_closed(count, max):
    if count < max:
        return "Corso aperto"
    else:
        return "Corso chiuso"


@blueprint.route('/courses')
def courses():
    all_course_prof = db.session.query(Course).join(User)
    return render_template('courses.html',
                           courses=all_course_prof)  # Course.query passa tutti i corsi


@blueprint.route('/<string:course>', methods=["GET", "POST"])
@login_required
def single_course(
        course):  # AGGIUNGERE CHE PRIMA DEVI ESSERE ISCRITTO AL CORSO per visualizzare lezioni nella route TODO ??? da mettere
    # utenti_user_totali = db.session.query(func.count(User._user_id)).where(User._role == "user").scalar()
    lesson_form = LessonsForm()
    token_form = TokenForm()
    course_subscription_form = CourseSubscription()
    certificate_form = PartecipationCertificate()
    remove_course_form = RemoveCourse()
    remove_lesson_form = RemoveLesson()
    modify_course_form = ModifyCourse()
    modify_lesson_form = ModifyLesson()
    info_corso = db.session.query(Course).filter_by(_name=course).join(User).first_or_404()

    course_lesson = db.session.query(Lesson).join(Course).filter(Course._name == course).order_by(
        Lesson._date).order_by(Lesson._start_hour)

    count = len(info_corso._users)
    progress_bar = 0
    attivo = course_open_or_closed(count, info_corso._max_student)

    numero_ore_fatte = timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0)
    zero = timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0)
    for x in course_lesson:
        if x._date < date.today():
            numero_ore_fatte += datetime.combine(date.today(), x._end_hour) - datetime.combine(date.today(),
                                                                                               x._start_hour)
    if numero_ore_fatte > zero:
        progress_bar = int(((numero_ore_fatte.seconds / 3600) / info_corso._n_hour) * 100)

    if lesson_form.submit1.data and lesson_form.validate_on_submit():
        Lesson(lesson_form.start_hour.data, lesson_form.end_hour.data, lesson_form.date.data, lesson_form.mode.data,
               lesson_form.link.data,
               lesson_form.structure.data, lesson_form.description.data, info_corso._course_id,
               secrets.token_hex(16)).save()
        flash("Lezione aggiunta", "success")
        return redirect(url_for('courses.single_course', course=course))

    if token_form.submit_token.data and token_form.validate_on_submit():
        l = db.session.query(Lesson).filter_by(_lesson_id=token_form.id.data).first()
        current_user.subscribe_lesson(l)
        flash("Hai registrato la tua presenza con successo")

    if course_subscription_form.submit_subcription_course.data and course_subscription_form.validate_on_submit():
        if current_user._role == "user":
            q = Course.query.filter_by(_name=course).first_or_404()
            current_user.subscribe_course(q)
            flash(f"Subscribe succesfull", "success")

    if certificate_form.submit_certificate.data and certificate_form.validate_on_submit():
        return certificate(course=info_corso._name, professor=info_corso._professor, ore=info_corso._n_hour)

    if remove_course_form.submit_remove_course.data and remove_course_form.validate_on_submit():
        q = Course.query.filter_by(_course_id=remove_course_form.id.data).first()
        q.delete()
        all_course_prof = db.session.query(Course).join(User)
        return render_template('courses.html',courses=all_course_prof)


    if remove_lesson_form.submit_remove_lesson.data and remove_lesson_form.validate_on_submit():
        q = Lesson.query.filter_by(_lesson_id=remove_lesson_form.id.data).first()
        q.delete()
        flash("lezione rimossa con successo")

    if modify_course_form.submit_modify_course.data and modify_course_form.validate_on_submit():
        print(modify_course_form.data)
        q = Course.query.filter_by(_course_id=modify_course_form.course_id.data).first()
        q.set_name(modify_course_form.name.data)
        q.set_description(modify_course_form.description.data)
        q.set_max_student(modify_course_form.max_student.data)
        q.set_n_hour(modify_course_form.n_hour.data)
        q.set_start_month(modify_course_form.start_month.data)
        q.set_end_month(modify_course_form.end_month.data)
        q.update()
        flash("Corso aggiornato con successo!")
        return redirect(url_for('courses.single_course', course=q._name))

    if modify_lesson_form.submit_modify_lesson.data and modify_lesson_form.validate_on_submit():
        q = Lesson.query.filter_by(_lesson_id=modify_lesson_form.lesson.data).first()
        q.set_start_hour(modify_lesson_form.start_hour.data)
        q.set_end_hour(modify_lesson_form.end_hour.data)
        q.set_mode(modify_lesson_form.mode.data)
        q.set_link(modify_lesson_form.link.data)
        q.set_structure(modify_lesson_form.structure.data)
        q.set_description(modify_lesson_form.description.data)
        q.update()
        flash("Lezione aggiornata con successo!")


    return render_template('single_course.html', Course=info_corso, attivo=attivo, progress_bar=progress_bar,
                           Lessons=course_lesson, lesson_form=lesson_form, token_form=token_form,
                           course_subscription_form=course_subscription_form, certificate_form=certificate_form,
                           remove_course_form=remove_course_form, remove_lesson_form=remove_lesson_form,
                           modify_course_form=modify_course_form, modify_lesson_form=modify_lesson_form)


@blueprint.route('/buildcourse', methods=("GET", "POST"))
@professor.require()  # la creazione del coros richiede di essere almeno professor
@login_required
def buildcourse():
    form = coursesForm()
    if form.validate_on_submit():
        Course(form.name.data, form.mode.data, form.description.data, form.max_student.data,
               form.min_student.data, form.n_hour.data, form.start_month.data, form.end_month.data,
               current_user._user_id).save()
        flash(f"Course created", "success")
        return redirect(url_for('courses.single_course', course=form.name.data))

    return render_template('buildcourse.html', name=current_user._user_id, form=form, title="Course",
                           btn_action="Create course")
