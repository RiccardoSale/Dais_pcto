# -*- coding: utf-8 -*-
"""The app module, containing the app factory function."""
from datetime import timedelta
from flask_principal import Principal
from sqlalchemy import MetaData
from flask_login import LoginManager
from flask import Flask
from dais_pcto.module_extensions import bcrypt, db, migrate
from dais_pcto import Lessons, Auth, Courses, BaseRoute, HSchool
from dais_pcto.settings import ProdConfig, DevConfig
from .Auth.models import User
from .Errors.errors import forbidden, not_found
from .HSchool.models import Hschool
from .Lessons.models import Lesson  

# Creazione
def create_app(config_object=DevConfig):
    """An application factory, as explained here:
    http://flask.pocoo.org/docs/patterns/appfactories/.
    :param config_object: The configuration object to use.
    """
    app = Flask(__name__.split('.')[0])
    app.url_map.strict_slashes = False
    app.config.from_object(config_object)
    app.permanent_session_lifetime = timedelta(minutes=30)
    register_extensions(app)
    meta = MetaData()
    meta.bind = db
    register_blueprints(app)
    login_manager = LoginManager()
    login_manager.session_protection = "strong"
    login_manager.login_message_category = "info"
    login_manager.login_view = 'Auth.login'
    login_manager.init_app(app)

    app.register_error_handler(404, not_found)
    app.register_error_handler(403, forbidden)

    # Si indica a flask login come trovare uno specifico utente dall'id che è salvato nella loro sessione dei cookie
    @login_manager.user_loader  
    def load_user(user_id):
        # Si usa l'id dell'utente per effettare la query ( chiave primaria)
        return User.query.get(int(user_id))

    return app


def register_extensions(app):
    """Register Flask extensions."""
    bcrypt.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    Principal(app)


def register_blueprints(app):
    """Register Flask blueprints."""
    app.register_blueprint(Auth.route.blueprint)
    app.register_blueprint(Courses.route.blueprint)
    app.register_blueprint(BaseRoute.route.blueprint)
    app.register_blueprint(Lessons.route.blueprint)
    app.register_blueprint(HSchool.route.blueprint)
