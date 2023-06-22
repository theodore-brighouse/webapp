from flask_wtf import FlaskForm
from wtforms import TextField, IntegerField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Email, EqualTo

class LoginForm(FlaskForm):
    email = TextField('Email', validators=[DataRequired("Please enter your email")])
    password = PasswordField('Password', validators=[DataRequired("Please enter your password")])
    submit = SubmitField('Login')

class SignupForm(FlaskForm):
    email = TextField('Email', validators=[DataRequired("Please enter your email"), Email("Please enter a valid email address")])
    password = PasswordField('Password', validators=[DataRequired("Please enter a password"), Length(min=8, message="Password must be at least eight characters long")])
    confirmPassword = PasswordField('Confirm Password', validators=[DataRequired("Please enter a password")])
    submit = SubmitField('Sign-Up')
