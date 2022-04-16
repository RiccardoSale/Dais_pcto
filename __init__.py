from datetime import timedelta
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt,generate_password_hash, check_password_hash
db = SQLAlchemy()
bcrypt = Bcrypt()

def create_app():
    from .models import User
    app = Flask(__name__)
    app.permanent_session_lifetime = timedelta(minutes=5)
    app.config['SECRET_KEY'] = 'secret-key-goes-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

    db.init_app(app)
    bcrypt.init_app(app)

    login_manager = LoginManager()
    login_manager.session_protection = "strong"
    login_manager.login_message_category = "info"
    login_manager.login_view = 'authentication.login'
    login_manager.init_app(app)

    @login_manager.user_loader #-> diciamo a flask login come trovare uno specifico utente dall id che e salvato nella loro sessione dei cookie
    def load_user(user_id):
        #usiamo l id per effettare la query ( chiave primaria)
        return User.query.get(int(user_id))

    # blueprint for auth routes in our app
    from .authentication import authentication as authentication_blueprint
    app.register_blueprint(authentication_blueprint)

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app

# app = Flask(__name__)
# app.permanent_session_lifetime = timedelta(minutes=5)
# app.config['SECRET_KEY'] = 'secret-key-goes-here'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
# db.init_app(app)
#
# # blueprint for auth routes in our app
# from .authentication import authentication as authentication_blueprint
# app.register_blueprint(authentication_blueprint)
#
# # blueprint for non-auth parts of app
# from .main import main as main_blueprint
# app.register_blueprint(main_blueprint)


# # @app.route("/")
# # def homepage():  # put application's code here
# #     return render_template("index.html")
# #
# # @app.route("/admin")
# def admin():
#     return redirect(url_for("hello_world"))
#
# @app.route("/login", methods=["POST", "GET"])
# def login():
#     if request.method == "POST":
#         session.permanent = True
#         user = request.form["loginrequest"]
#         session["user"] = user
#
#         usr = users(user,"mailposticcia@gmail.com")
#         db.session.add(usr)
#         db.session.commit()
#
#         return redirect(url_for("user"))
#     else:
#         if "user" in session:
#             return redirect(url_for("user"))
#         return render_template("login.html")
#
# @app.route("/user")
# def user():
#     if "user" in session:
#         user = session["user"]
#         return f"<h1>{user}</h1>"
#     else:
#         return redirect(url_for("login"))
#
# @app.route("/logout")
# def logout():
#     session.pop("user", None)
#     return redirect(url_for("login"))
#
# @app.route("/view")
# def view():
#     return render_template("view.html",values=users.query.all())
#
# if __name__ == '__main__':
#     app.run(debug=True)
