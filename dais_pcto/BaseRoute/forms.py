from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import Length, Regexp, Email, InputRequired, Optional


class EditProfile(FlaskForm):
    # username = StringField(
    #     validators=[Length(3, 64, message="Please provide a valid username"), Optional(), Regexp(
    #         "^[A-Za-z0-9]*$",
    #         0,
    #         "Usernames must have only letters, " "numbers, dots or underscores",
    #     )]
    # )
    email = StringField(validators=[Email(), Length(1, 64), Optional()])
    new_password = PasswordField(validators=[Length(8, 72), Optional()])
    old_password = PasswordField(
        validators=[InputRequired(message="password necessaria per cambio credenziali"), Length(8, 72)])
    name = StringField(validators=[Length(3, 64, message="Please provide a valid name"), Optional(), Regexp(
        "^[A-Za-z][A-Za-z0-9_.]*$",  # trovare regex per lettere italiane e straniere
        0,
        "Name can have only letters",
    )])
    surname = StringField(
        validators=[Length(3, 20, message="Please provide a valid name"), Optional(), Regexp(
            "^[A-Za-z][A-Za-z0-9_.]*$",
            0,
            "Surname can have only letters",
        )])
