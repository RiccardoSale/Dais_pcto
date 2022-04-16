from flask import Blueprint, redirect, url_for,flash,render_template
from flask_login import login_required, current_user
from .models import Courses
from flask_wtf import FlaskForm
from sqlalchemy.testing import db
from werkzeug.routing import BuildError
from wtforms import StringField, PasswordField
from wtforms.validators import Email, InputRequired, Length, Regexp
from sqlalchemy.exc import (IntegrityError, DataError, DatabaseError, InterfaceError, InvalidRequestError, )
from . import db

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html',
                           name=current_user.username)  # ->passo al render il nome dell'utente in modo da poterlo usare come dato all'interno del template


@main.route('/courses')
@login_required
def courses():
    return render_template('courses.html', name=current_user.username, courses=Courses.query)


@main.route('/administration', methods=("GET", "POST"))
@login_required
def administration():
    form = courses_form()
    if form.validate_on_submit():
        try:
            name = form.name.data
            department = form.department.data
            professor = form.professor.data
            newcourses = Courses(name=name,department=department,professor=professor)
            db.session.add(newcourses)
            db.session.commit()
            flash(f"Course created", "success")
            return redirect(url_for('main.courses'))

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
    return render_template('signup.html', name=current_user.username,form=form,title="Courses",btn_action="Create course")


class courses_form(FlaskForm):
    name = StringField(validators=[InputRequired(), Length(1, 64),
                                   Regexp("^[A-Za-z][A-Za-z0-9_.]*$", 0, "Name of the courses is not valid"), ])
    department = StringField(validators=[InputRequired(), Length(1, 64),
                                         Regexp("[A-Za-z]*", 0, "Name of deparment can contain only letters")])
    professor = StringField(
        validators=[InputRequired(), Length(1, 64), Regexp("[A-Za-z]*", 0, "Professor name can contain only letters")])
