from datetime import datetime

from dais_pcto.Auth.route import admin, professor
from dais_pcto.Courses.models import Course
from flask import Blueprint, url_for, current_app, redirect, g, flash, render_template
from flask_login import login_required, logout_user, login_user, current_user
from werkzeug.routing import BuildError
from sqlalchemy.exc import (IntegrityError, DataError, DatabaseError, InterfaceError, InvalidRequestError, )
from dais_pcto.app import db
from .forms import coursesForm
from ..Auth.models import User

blueprint = Blueprint('courses', __name__)


@blueprint.route('/courses')
def courses():
    all_course_prof = db.session.query(Course).join(User)
    return render_template('courses.html',
                           courses=all_course_prof)  # Course.query passa tutti i corsi


@blueprint.route('/courses/<string:course>', methods=["GET"])
@login_required
def single_course(course):
    q = db.session.Course.query.filter_by(_name=course).join(User).first_or_404()
    count = len(q._users)  ##len o query ???
    if count < q._max_student:
        attivo = "Corso aperto"
    else:
        attivo = "Corso chiuso"

    progress_bar = 10
    return render_template('single_course.html', Course=q, attivo=attivo, progress_bar=progress_bar)


@blueprint.route('/courses/<string:course>', methods=["POST"])
@login_required
def single_course_post(course):  # ISCRIZIONE AL CORSO
    q = Course.query.filter_by(_name=course).join(User).first_or_404()  # ORM
    try:
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

    return render_template('single_course.html', Course=q)


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

    return render_template('signup.html', name=current_user._username, form=form, title="Course",
                           btn_action="Create course")
