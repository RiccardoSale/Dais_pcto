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
from ..module_extensions import CRUDMixin

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
    return render_template("signup.html", form=form, text="Login", title="Login", btn_action="Login")


@blueprint.route("/signup", methods=("GET", "POST"))
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        email = form.email.data
        role = "user"
        if "@unive.it" in email:
            role = "professor"
        if "@segunive.it" in email:
            role = "admin"
        # decode necessario altrimenti con postgres la password viene "hashata 2 volte"
        User(form.name.data, form.surname.data, email, bcrypt.generate_password_hash(form.password.data).decode('utf8'),
             role).save()
        flash(f"Account Succesfully created", "success")
        return redirect(url_for('Auth.login'))

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
