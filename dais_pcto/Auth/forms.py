from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, DateField, PasswordField
from wtforms.validators import InputRequired, Length, Regexp, Email, ValidationError, Optional
from .models import user_with_email


class LoginForm(FlaskForm):
    email = StringField(validators=[InputRequired(), Email(), Length(1, 64)])
    password = PasswordField(validators=[Optional()])


class SignupForm(FlaskForm):
    email = StringField(validators=[InputRequired(), Email(), Length(1, 64)])
    password = PasswordField(validators=[InputRequired(), Length(8, 72)])
    name = StringField(validators=[InputRequired(), Length(3, 64, message="Please provide a valid name"), Regexp(
        "^[A-Za-z][A-Za-z0-9_.]*$",  # trovare regex per lettere italiane e straniere
        0,
        "Name can have only letters",
    )])
    surname = StringField(
        validators=[InputRequired(), Length(3, 20, message="Please provide a valid name"), Regexp(
            "^[A-Za-z][A-Za-z0-9_.]*$",
            0,
            "Surname can have only letters",
        )])

    def validate_email(self, field):
        if user_with_email(field.data).first():
            raise ValidationError("Email già registrata!")



