from flask import Blueprint, render_template, redirect, url_for, request, flash
from . import db
from . import bcrypt
from flask_login import login_user, login_required, logout_user
from sqlalchemy.exc import (IntegrityError, DataError, DatabaseError, InterfaceError, InvalidRequestError, )
from werkzeug.routing import BuildError
from wtforms import (StringField, PasswordField, BooleanField, IntegerField, DateField, TextAreaField)
from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, Length, EqualTo, Email, Regexp, Optional
import email_validator
from flask_login import current_user
from wtforms import ValidationError, validators
from .models import User
from flask_bcrypt import Bcrypt, generate_password_hash, check_password_hash

authentication = Blueprint('authentication', __name__)


@authentication.route("/login", methods=("GET", "POST"))
def login():
    form = login_form()

    if form.validate_on_submit():
        try:
            user = User.query.filter_by(email=form.email.data).first()
            if user is not None:
                if check_password_hash(user.password, form.password.data):
                    login_user(user)
                    return redirect(url_for('main.profile'))
                else:
                    flash("Invalid Username or password!", "danger")
            else:
                flash("Invalid Username or password!", "danger")
        except Exception as e:
            flash(e, "danger")

    return render_template("signup.html", form=form, text="Login", title="Login", btn_action="Login")


@authentication.route("/signup", methods=("GET", "POST"))
def signup():
    form = signup_form()
    if form.validate_on_submit():
        try:
            email = form.email.data
            password = form.password.data
            username = form.username.data
            newuser = User(username=username, email=email, password=bcrypt.generate_password_hash(password), )
            db.session.add(newuser)
            db.session.commit()
            flash(f"Account Succesfully created", "success")
            return redirect(url_for('authentication.login'))

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
    return render_template("signup.html", form=form, text="Create account", title="Register",
                           btn_action="Register account")


@authentication.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


class login_form(FlaskForm):
    email = StringField(validators=[InputRequired(), Email(), Length(1, 64)])
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=72)])
    # Placeholder labels to enable form rendering
    username = StringField(
        validators=[Optional()]
    )


class signup_form(FlaskForm):
    username = StringField(
        validators=[
            InputRequired(),
            Length(3, 20, message="Please provide a valid name"),
            Regexp(
                "^[A-Za-z][A-Za-z0-9_.]*$",
                0,
                "Usernames must have only letters, " "numbers, dots or underscores",
            ),
        ]
    )
    email = StringField(validators=[InputRequired(), Email(), Length(1, 64)])
    password = PasswordField(validators=[InputRequired(), Length(8, 72)])

    def validate_email(self, email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError("Email already registered!")
