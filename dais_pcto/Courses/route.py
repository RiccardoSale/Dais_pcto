import secrets
from datetime import datetime

from sqlalchemy import func

from dais_pcto.Auth.route import admin, professor
from dais_pcto.Courses.models import Course
from flask import Blueprint, url_for, current_app, redirect, g, flash, render_template
from flask_login import login_required, logout_user, login_user, current_user
from werkzeug.routing import BuildError
from sqlalchemy.exc import (IntegrityError, DataError, DatabaseError, InterfaceError, InvalidRequestError, )
from dais_pcto.app import db
from .forms import coursesForm
from ..Auth.models import User
from dais_pcto import Lessons
from ..Lessons.forms import LessonsForm
from ..Lessons.models import Lesson

blueprint = Blueprint('courses', __name__)


@blueprint.route('/courses')
def courses():
    all_course_prof = db.session.query(Course).join(User)
    return render_template('courses.html',
                           courses=all_course_prof)  # Course.query passa tutti i corsi


@blueprint.route('/courses/<string:course>', methods=["GET","POST"])
@login_required
def single_course(course):
    form = LessonsForm()
    info_corso = db.session.query(Course).filter_by(_name=course).join(User).first_or_404()
    utenti_user_totali = db.session.query(func.count(User._user_id)).where(User._role=="user").scalar()
    print("utenti user totali" )
    print(utenti_user_totali)
    count = len(info_corso._users)  ##len o query ???
    print("utenti iscritti al corso" )
    print(count)
    progress_bar=0
    if count> 0:
        progress_bar = (utenti_user_totali /count )*10
    print(progress_bar)
    if count < info_corso._max_student:
        attivo = "Corso aperto"
    else:
        attivo = "Corso chiuso"

    if form.validate_on_submit():
        new_lesson = Lesson(form.start_hour.data, form.end_hour.data, form.date.data, form.mode.data, form.link.data,
                            form.structure.data, form.description.data,info_corso._course_id,secrets.token_hex(16))
        db.session.add(new_lesson)
        db.session.commit()
        flash("Lezione aggiunta", "success")
        return redirect(url_for('courses.single_course', course=course))

    if current_user._role == "user":
        q = Course.query.filter_by(_name=course).join(User).first_or_404()  # ORM
        val = True
        for test in current_user._courses:
            if test == q:
                val = False
        if not val:
            flash(f'Sei già iscritto a questo corso', "warning")
        else:
            if len(q._users) < q._max_student:  # Controllo se numero utenti al corso minore del numero massimo di studenti
                current_user._courses.append(q)
                db.session.commit()
                flash(f"Subscribe succesfull", "success")
            else:
                flash(f'Non ci sono più posti disponibili', "warning")

    # course_lesson = db.session.query(Lessons).filter_by(course=info_corso._name)
    course_lesson = info_corso._lessons
    print(course_lesson)
    return render_template('single_course.html', Course=info_corso, attivo=attivo, progress_bar=progress_bar,
                           Lessons=course_lesson, form=form)


@blueprint.route('/administration', methods=("GET", "POST"))
@professor.require()  # la creazione del coros richiede di essere almeno professor
# come far accedere admin da vedere ???!
@login_required
def administration():
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

    return render_template('signup.html', name=current_user._user_id, form=form, title="Course",
                           btn_action="Create course")
