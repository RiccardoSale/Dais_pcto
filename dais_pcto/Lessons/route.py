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

blueprint = Blueprint('lessons', __name__)



# @blueprint.route('/le', methods=("GET", "POST"))
# @admin.require(http_exception=403)  # la creazione del coros richiede di essere almeno professor
# # come far accedere admin da vedere ???!
# @login_required
# def lesson():
#     print(current_user.r_courses_prof)
#     form = coursesForm()
#     if form.validate_on_submit():
#         try:
#             name = form.name.data
#             # render_professor= current_user.name +" " + current_user.surname
#             mode = form.mode.data  # modalita 0 = online modalità 1 = presenza modalita 3 = blendend
#             description = form.description.data
#             max_student = form.max_student.data
#             min_student = form.min_student.data
#             n_hour = form.n_hour.data
#             start_month = form.start_month.data
#             end_month = form.end_month.data
#             flag = True
#             if max_student < min_student:
#                 flag = False
#                 flash("Il numero di studenti minimi deve essere minore del numero di studenti massimi", "warning")
#             if str(end_month) < str(start_month):
#                 flag = False
#                 flash("La data di fine del corso deve essere successiva alla data di inizio del corso", "warning")
#             if flag:
#                 newcourses = Course(name=name, professor=current_user.id, mode=mode, description=description,
#                                     max_student=max_student, min_student=min_student, n_hour=n_hour,
#                                     start_month=start_month, end_month=end_month)
#                 db.session.add(newcourses)
#                 # non serve backref aggiunge in automatico
#                 # current_user.r_courses_prof.append(newcourses)
#                 db.session.commit()
#                 flash(f"Course created", "success")
#                 return redirect(url_for('courses.single_course', course=name))
#             else:
#                 return render_template('signup.html', name=current_user.username, form=form, title="Course",
#                                        btn_action="Create course")
#
#         except InvalidRequestError:
#             db.session.rollback()
#             flash(f"Something went wrong!", "danger")
#         except IntegrityError:
#             db.session.rollback()
#             flash(f"An error has occurred!.", "warning")
#         except DataError:
#             db.session.rollback()
#             flash(f"Invalid Entry", "warning")
#         except InterfaceError:
#             db.session.rollback()
#             flash(f"Error connecting to the database", "danger")
#         except DatabaseError:
#             db.session.rollback()
#             flash(f"Error connecting to the database", "danger")
#         except BuildError:
#             db.session.rollback()
#             flash(f"An error occured !", "danger")
#     return render_template('signup.html', name=current_user.username, form=form, title="Course",
#                            btn_action="Create course")