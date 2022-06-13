from dais_pcto.Auth.route import admin
from flask import Blueprint, url_for, current_app, redirect, g, flash, render_template
from flask_login import login_required, logout_user, login_user ,current_user
from werkzeug.routing import BuildError
from flask_wtf import FlaskForm
from sqlalchemy.exc import (IntegrityError, DataError, DatabaseError, InterfaceError, InvalidRequestError, )
from wtforms import StringField, PasswordField ,ValidationError
from wtforms.validators import InputRequired, Email, Length, Regexp
from dais_pcto.app import db

blueprint = Blueprint('lessons', __name__)
