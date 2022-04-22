from flask import Blueprint, url_for, current_app, redirect, g, flash, render_template
from flask_login import login_required, logout_user, login_user
from flask_principal import Permission, RoleNeed, ActionNeed, identity_loaded, identity_changed, AnonymousIdentity, \
    Identity
from werkzeug.routing import BuildError
from flask_wtf import FlaskForm
from flask_bcrypt import Bcrypt, generate_password_hash, check_password_hash
from sqlalchemy.exc import (IntegrityError, DataError, DatabaseError, InterfaceError, InvalidRequestError, )
from wtforms import StringField, PasswordField, ValidationError
from wtforms.validators import InputRequired, Email, Length, Regexp, Optional
from dais_pcto.Auth.models import User
from dais_pcto.app import db
from dais_pcto.module_extensions import bcrypt

blueprint = Blueprint('Auth', __name__)

be_admin = RoleNeed('admin')
be_editor = RoleNeed('editor')
to_sign_in = ActionNeed('sign in')

# Permissions
user = Permission(to_sign_in)
user.description = "User's permissions"
editor = Permission(be_editor)
editor.description = "Editor's permissions"
admin = Permission(be_admin)
admin.description = "Admin's permissions"

admin_permission = Permission(RoleNeed('admin'))
professor_permission = Permission(RoleNeed('professor'))


@blueprint.route("/login", methods=("GET", "POST"))
def login():
    form = LoginForm()
    print("ciaociao")
    if form.validate_on_submit():
        try:
            q = User.query.filter_by(email=form.email.data).first()
            if q is not None:
                if check_password_hash(q.password, form.password.data):
                    login_user(q)
                    identity_changed.send(current_app._get_current_object(), identity=Identity(q.role))
                    return redirect(url_for('BaseRoute.profile'))
                else:
                    flash("Invalid Username or password!", "danger")
            else:
                flash("Invalid Username or password!", "danger")
        except Exception as e:
            flash(e, "danger")
    return render_template("signup.html", form=form, text="Login", title="Login", btn_action="Login")


@blueprint.route("/signup", methods=("GET", "POST"))
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        try:
            email = form.email.data
            password = form.password.data
            username = form.username.data
            newuser = User(username=username, email=email, password=bcrypt.generate_password_hash(password), )
            db.session.add(newuser)
            db.session.commit()
            flash(f"Account Succesfully created", "success")
            return redirect(url_for('Auth.login'))

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


@blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    identity_changed.send(current_app._get_current_object(), identity=AnonymousIdentity())
    return redirect(url_for('BaseRoute.index'))


class LoginForm(FlaskForm):
    email = StringField(validators=[InputRequired(), Email(), Length(1, 64)])
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=72)])
    # Placeholder labels to enable form rendering
    username = StringField(
        validators=[Optional()]
    )


class SignupForm(FlaskForm):
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


@identity_loaded.connect
def on_identity_loaded(sender, identity):
    needs = []

    if identity.id == 'admin':
        needs.append(be_admin)

    for n in needs:
        g.identity.provides.add(n)
