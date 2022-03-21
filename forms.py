from random import choices
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectMultipleField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_user = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired(), Length(min=5, max=10)])
    lastname = StringField('Last Name', validators=[DataRequired(), Length(min=5, max=10)])
    city = StringField('City', [DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    repeat_password = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    options=['12 available options:', 'French', 'Spanish', 'English', 'Portuguese', 'Chinese', 'German','Khoisan', 'Korean', 'Swahili', 'Japanese', 'Russian', 'Arabic']
    languages = SelectMultipleField('Select your native and fluent language(s)', validators=[DataRequired()], choices=options)
    other_languages = SelectMultipleField('Select the language(s) you want to learn', validators=[DataRequired()], choices=options)
    interests = TextAreaField('Describe your Interests and ideal language exchange partner', validators=[DataRequired(), Length(max=300)])
    submit = SubmitField('Confirm Registration')
