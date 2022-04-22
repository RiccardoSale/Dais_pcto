from dais_pcto.Auth.route import admin
from dais_pcto.Courses.models import Course
from flask import Blueprint, url_for, current_app, redirect, g, flash, render_template
from flask_login import login_required, logout_user, login_user ,current_user
from werkzeug.routing import BuildError
from flask_wtf import FlaskForm
from sqlalchemy.exc import (IntegrityError, DataError, DatabaseError, InterfaceError, InvalidRequestError, )
from wtforms import StringField, PasswordField ,ValidationError
from wtforms.validators import InputRequired, Email, Length, Regexp
from dais_pcto.app import db

blueprint = Blueprint('courses', __name__)


@blueprint.route('/courses')
@login_required
def courses():
    return render_template('courses.html', name=current_user.username,
                           courses=Course.query)  # Course.query passa tutti i corsi


@blueprint.route('/courses/<string:course>', methods=["GET"])
def single_course(course):
    q = Course.query.filter_by(name=course).first_or_404()  # ORM
    id = q.id
    name = course
    department = q.department
    professor = q.professor
    return render_template('single_course.html', id=id, name=name, department=department, professor=professor)


@blueprint.route('/courses/<string:course>', methods=["POST"])
def single_course_post(course):
    q = Course.query.filter_by(name=course).first_or_404()  # ORM
    user = current_user
    q2 = Course.users
    name = course
    department = q.department
    professor = q.professor
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

    return render_template('single_course.html', id=id, name=name, department=department, professor=professor)


@blueprint.route('/administration', methods=("GET", "POST"))
@admin.require(http_exception=403)
@login_required
def administration():
    form = coursesForm()
    if form.validate_on_submit():
        try:
            name = form.name.data
            department = form.department.data
            professor = form.professor.data
            newcourses = Course(name=name, department=department, professor=professor)
            db.session.add(newcourses)
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


class coursesForm(FlaskForm):
    name = StringField(validators=[InputRequired(), Length(1, 64),
                                   Regexp("^[A-Za-z][A-Za-z0-9_.]*$", 0, "Name of the courses is not valid"), ])
    department = StringField(validators=[InputRequired(), Length(1, 64),
                                         Regexp("[A-Za-z]*", 0, "Name of deparment can contain only letters")])
    professor = StringField(
        validators=[InputRequired(), Length(1, 64), Regexp("[A-Za-z]*", 0, "Professor name can contain only letters")])