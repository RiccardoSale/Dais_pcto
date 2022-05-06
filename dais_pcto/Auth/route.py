from flask import Blueprint, url_for, current_app, redirect, g, flash, render_template
from flask_login import login_required, logout_user, login_user
from flask_principal import Permission, RoleNeed, ActionNeed, identity_loaded, identity_changed, AnonymousIdentity, \
    Identity
from werkzeug.routing import BuildError, ValidationError
from flask_bcrypt import Bcrypt, generate_password_hash, check_password_hash
from sqlalchemy.exc import (IntegrityError, DataError, DatabaseError, InterfaceError, InvalidRequestError, )
from dais_pcto.Auth.models import User
from dais_pcto.app import db
from dais_pcto.module_extensions import bcrypt
from .forms import LoginForm, SignupForm

blueprint = Blueprint('Auth', __name__)

be_admin = RoleNeed('admin')
be_professor = RoleNeed('professor')

# Permissions
professor = Permission(be_professor)
professor.description = "Professor permissions"
admin = Permission(be_admin)
admin.description = "Admin's permissions"


@blueprint.route("/login", methods=("GET", "POST"))
def login():
    form = LoginForm()
    if form.validate_on_submit():
        try:
            q = User.query.filter_by(_email=form.email.data).first()
            if q is not None:
                if check_password_hash(q._password, form.password.data):
                    login_user(q)
                    identity_changed.send(current_app._get_current_object(), identity=Identity(q._role))
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
            role = "user"
            if "@unive.it" in email:
                role = "professor"
            if "@segunive.it" in email:
                role = "admin"
            new_user = User(form.name.data, form.surname.data, email,
                            bcrypt.generate_password_hash(form.password.data).decode('utf8'),
                            role)  # decode necessario altrimenti con postgres la password viene "hashata 2 volte"
            db.session.add(new_user)
            db.session.commit()
            flash(f"Account Succesfully created", "success")
            return redirect(url_for('Auth.login'))

        except InvalidRequestError:
            db.session.rollback()
            flash(f"Something went wrong!", "danger")
        except IntegrityError:
            db.session.rollback()
            flash(f"User or email already exits!", "warning")
        except DataError:
            db.session.rollback()
            flash(f"Invalid Entry", "warning")
        except InterfaceError:
            db.session.rollback()
            flash(f"Error connecting to the database", "danger")
            # db.session.rollback()
            # flash(f"Error connecting to the database", "danger")
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


@identity_loaded.connect
def on_identity_loaded(sender, identity):
    needs = []
    if identity.id == 'admin':
        needs.append(be_admin)
        needs.append(be_professor)
    if identity.id == 'professor':
        needs.append(be_professor)

    for n in needs:
        g.identity.provides.add(n)
