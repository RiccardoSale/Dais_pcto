from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, DateField, PasswordField
from wtforms.validators import InputRequired, Length, Regexp, Email, ValidationError, Optional
from .models import User


class LoginForm(FlaskForm):
    email = StringField(validators=[InputRequired(), Email(), Length(1, 64)])
    password = PasswordField(validators=[Optional()])
    # username = StringField(
    #     validators=[InputRequired(), Length(3, 64, message="Please provide a valid username"), Regexp(
    #         "^[A-Za-z0-9]*$",
    #         0,
    #         "Usernames must have only letters, " "numbers, dots or underscores",
    #     )]
    # )


def validate_username(username):#capire se usarlo ha senso o effettuare integrity error ->al posto di raise cosa usare
    if User.query.filter_by(username=username).first():
        raise ValidationError("Username already registered")


def validate_email(email):
    if User.query.filter_by(email=email).first():
        raise ValidationError("Email already registered!")


class SignupForm(FlaskForm):
    username = StringField(
        validators=[InputRequired(), Length(3, 64, message="Please provide a valid username"), Regexp(
            "^[A-Za-z0-9]*$",
            0,
            "Usernames must have only letters, " "numbers, dots or underscores",
        ),
                    ]
    )
    email = StringField(validators=[InputRequired(), Email(), Length(1, 64)])
    password = PasswordField(validators=[InputRequired(), Length(8, 72)])
    name = StringField(validators=[InputRequired(), Length(3, 64, message="Please provide a valid name"), Regexp(
        "^[A-Za-z][A-Za-z0-9_.]*$",#trovare regex per lettere italiane e straniere
        0,
        "Name can have only letters",
    )])
    surname = StringField(
        validators=[InputRequired(), Length(3, 20, message="Please provide a valid name"), Regexp(
            "^[A-Za-z][A-Za-z0-9_.]*$",
            0,
            "Surname can have only letters",
        )])
