from flask import Blueprint, url_for, current_app, redirect, g, flash, render_template
from flask_login import login_required, logout_user, login_user
from flask_principal import Permission, RoleNeed, ActionNeed, identity_loaded, identity_changed, AnonymousIdentity, \
    Identity
from werkzeug.routing import BuildError, ValidationError
from flask_bcrypt import Bcrypt, generate_password_hash, check_password_hash
from sqlalchemy.exc import (IntegrityError, DataError, DatabaseError, InterfaceError, InvalidRequestError, )
from dais_pcto.Auth.models import User, user_with_email
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
# Controllo sul login
def login():
    # Recupero dei dati inseriti nel form
    form = LoginForm()
    # Se i dati inseriti sono validi per il login
    if form.validate_on_submit():
        q = user_with_email(form.email.data).first()
        # Controllo della corrispondenza dei dati con un eventuale utente
        if q is not None:
            # Controllo della password inserita
            if check_password_hash(q._password, form.password.data):
                login_user(q)
                identity_changed.send(current_app._get_current_object(), identity=Identity(q._role))
                # Se è tutto corretto si accede alla propria pagina profilo
                return redirect(url_for('BaseRoute.profile'))
            else:
                # Si mostra un avviso per indicare che qualcosa è andato storto
                flash("Controlla lo username o la password inseriti!", "danger")
        else:
            flash("Controlla lo username o la password inseriti!", "danger")
    # Rimando alla pagina di iscrizione
    return render_template("signup.html", form=form, text="Login", title="Login", btn_action="Login")


@blueprint.route("/signup", methods=("GET", "POST"))
# Controllo sull'iscrizione
def signup():
    # Recupero dei dati inseriti nel form
    form = SignupForm()
    # Se i dati inseriti sono validi per l'iscrizione
    if form.validate_on_submit():
        # Si impostano i campi correttamente
        email = form.email.data
        role = "user"
        if "@unive.it" in email:
            role = "professor"
        if "@segunive.it" in email:
            role = "admin"
        # Il 'decode' risulta necessario altrimenti con Postgres la password viene "hashata" 2 volte
        User(form.name.data, form.surname.data, email, bcrypt.generate_password_hash(form.password.data).decode('utf8'),
             role).save()
        flash("L'account è stato creato con successo!", "success")
        # Una volta che l'utente si è iscritto lo si fa loggare per accedere all'applicazione
        return redirect(url_for('Auth.login'))
    # Se i dati inseriti non sono validi si rimanda alla pagina di iscrizione
    return render_template("signup.html", form=form, text="Create account", title="Register",
                           btn_action="Register account")


@blueprint.route('/logout')
@login_required
# Funzione per uscire dalla propria pagina
def logout():
    logout_user()
    identity_changed.send(current_app._get_current_object(), identity=AnonymousIdentity())
    # Ritorno alla pagina iniziale
    return redirect(url_for('BaseRoute.index'))

# Assegnazione dei ruoli a un utente
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
