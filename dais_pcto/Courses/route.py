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
from ..Courses.forms import CourseSubscription
from ..Lessons.forms import LessonsForm, TokenForm
from ..Lessons.models import Lesson

blueprint = Blueprint('courses', __name__, )


def course_open_or_closed(course, count, max):
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
        course):  # AGGIUNGERE CHE PRIMA DEVI ESSERE ISCRITTO AL CORSO per visualizzare lezioni nella route TODO
    form = LessonsForm()
    form2 = TokenForm()
    form3 = CourseSubscription()
    form4 = PartecipationCertificate()
    info_corso = db.session.query(Course).filter_by(_name=course).join(User).first_or_404()
    utenti_user_totali = db.session.query(func.count(User._user_id)).where(User._role == "user").scalar()


    course_lesson = db.session.query(Lesson).join(Course).filter(Course._name==course).order_by(Lesson._date).order_by(Lesson._start_hour)
    #course_lesson = info_corso._lessons.order_by(desc(Lesson._date))
    count = len(info_corso._users)  ##len o query ???
    progress_bar = 0

    numero_ore_fatte = timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0)
    zero = timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0)
    for x in course_lesson:
        if x._date < date.today():
            numero_ore_fatte += datetime.combine(date.today(), x._end_hour) - datetime.combine(date.today(),
                                                                                               x._start_hour)

    if numero_ore_fatte > zero:
        progress_bar = int(((numero_ore_fatte.seconds / 3600) / info_corso._n_hour) * 100)

    # if count > 0:
    #     progress_bar = (utenti_user_totali / count) * 10
    # print(progress_bar)

    attivo = course_open_or_closed(course, count, info_corso._max_student)

    if form.submit1.data and form.validate_on_submit():
        new_lesson = Lesson(form.start_hour.data, form.end_hour.data, form.date.data, form.mode.data, form.link.data,
                            form.structure.data, form.description.data, info_corso._course_id, secrets.token_hex(16))
        db.session.add(new_lesson)
        db.session.commit()
        flash("Lezione aggiunta", "success")
        return redirect(url_for('courses.single_course', course=course))

    if form2.submit2.data and form2.validate_on_submit():
        l = db.session.query(Lesson).filter_by(_lesson_id=form2.id.data).first()
        current_user._lessons.append(l)
        db.session.commit()
        flash("Hai registrato la tua presenza con successo")

    if form3.submit3.data and form3.validate_on_submit():
        if current_user._role == "user":
            q = Course.query.filter_by(_name=course).first_or_404()
            current_user._courses.append(q)
            db.session.commit()
            flash(f"Subscribe succesfull", "success")

    if form4.submit4.data and form4.validate_on_submit():
        return certificate(course=info_corso._name, professor=info_corso._professor, ore=info_corso._n_hour)

    return render_template('single_course.html', Course=info_corso, attivo=attivo, progress_bar=progress_bar,
                           Lessons=course_lesson, form=form, form2=form2, form3=form3, form4=form4)


@blueprint.route('/buildcourse', methods=("GET", "POST"))
@professor.require()  # la creazione del coros richiede di essere almeno professor
# come far accedere admin da vedere ???!
@login_required
def buildcourse():
    form = coursesForm()
    if form.validate_on_submit():
        newcourses = Course(form.name.data, form.mode.data, form.description.data, form.max_student.data,
                            form.min_student.data, form.n_hour.data, form.start_month.data, form.end_month.data,
                            current_user._user_id)
        db.session.add(newcourses)
        # non serve backref aggiunge in automatico
        # current_user.r_courses_prof.append(newcourses)
        db.session.commit()
        flash(f"Course created", "success")
        return redirect(url_for('courses.single_course', course=form.name.data))

    return render_template('buildcourse.html', name=current_user._user_id, form=form, title="Course",
                           btn_action="Create course")
