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
@login_required
def courses():
    all_course_prof = db.session.query(Course).join(User)
    return render_template('courses.html',
                           courses=all_course_prof)  # Course.query passa tutti i corsi


@blueprint.route('/courses/<string:course>', methods=["GET"])
def single_course(course):
    q = Course.query.filter_by(name=course).first_or_404()  # ORM
    name = course
    prof = q.professor
    return render_template('single_course.html', name=name, professor=prof)


@blueprint.route('/courses/<string:course>', methods=["POST"])
def single_course_post(course):
    q = Course.query.filter_by(name=course).first_or_404()  # ORM
    user = current_user
    q2 = Course.users
    name = course
    # professor = q.professor
    # try:    # DA FINIREEEEE
    #     if q2 is not None:
    try:
        user.courses.append(q)
        db.session.commit()
        flash(f"Subscribe succesfull", "success")
    #     else:
    #         flash(f"sei già iscritto succesfull", "danger")
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

    return render_template('single_course.html', id=id, name=name, professor=professor)


@blueprint.route('/administration', methods=("GET", "POST"))
@professor.require(http_exception=403)  # la creazione del coros richiede di essere almeno professor
# come far accedere admin da vedere ???!
@login_required
def administration():
    print(current_user.r_courses_prof)
    form = coursesForm()
    if form.validate_on_submit():
        try:
            name = form.name.data
            # render_professor= current_user.name +" " + current_user.surname
            mode = form.mode.data  # modalita 0 = online modalità 1 = presenza modalita 3 = blendend
            description = form.description.data
            max_student = form.max_student.data
            min_student = form.min_student.data
            n_hour = form.n_hour.data
            start_month = form.start_month.data
            end_month = form.end_month.data
            newcourses = Course(name=name, professor=current_user.id, mode=mode, description=description,
                                max_student=max_student, min_student=min_student, n_hour=n_hour,
                                start_month=start_month, end_month=end_month)
            db.session.add(newcourses)
            #non serve backref aggiunge in automatico
            #current_user.r_courses_prof.append(newcourses)
            db.session.commit()
            flash(f"Course created", "success")
            return redirect(url_for('courses.single_course', course=name))

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
    return render_template('signup.html', name=current_user.username, form=form, title="Course",
                           btn_action="Create course")
