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
from .HSchool.models import Hschool
from .Lessons.models import Lesson #NECESSARIO PER FAR VEDERE TABELLA ANCHE SE RISULTANO IMPORT INUSATI !!!!


# from conduit.exceptions import InvalidUsage
# comandi init db
# from dais_pcto.app import create_app
# from dais_pcto.module_extensions import db
# db.create_all(app=create_app())
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
    # register_errorhandlers(app)
    # register_shellcontext(app)
    # register_commands(app)
    login_manager = LoginManager()
    login_manager.session_protection = "strong"
    login_manager.login_message_category = "info"
    login_manager.login_view = 'Auth.login'
    login_manager.init_app(app)

    # db.create_all()
    @login_manager.user_loader  # -> diciamo a flask login come trovare uno specifico utente dall id che e salvato nella loro sessione dei cookie
    def load_user(user_id):
        # usiamo l id per effettare la query ( chiave primaria)
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

# def register_errorhandlers(app):
#
#     def errorhandler(error):
#         response = error.to_json()
#         response.status_code = error.status_code
#         return response
#
#     app.errorhandler(InvalidUsage)(errorhandler)


# def register_shellcontext(app):
#     """Register shell context objects."""
#     def shell_context():
#         """Shell context objects."""
#         return {
#             'db': db,
#             'User': user.models.User,
#             'UserProfile': profile.models.UserProfile,
#             'Article': articles.models.Article,
#             'Tag': articles.models.Tags,
#             'Comment': articles.models.Comment,
#         }
#
#     app.shell_context_processor(shell_context)
#
#
# def register_commands(app):
#     """Register Click commands."""
#     app.cli.add_command(commands.test)
#     app.cli.add_command(commands.lint)
#     app.cli.add_command(commands.clean)
#     app.cli.add_command(commands.urls)
