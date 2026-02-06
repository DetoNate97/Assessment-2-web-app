from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError

class RegisterForm(FlaskForm):
    FloatingUsername = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)], render_kw={"placeholder": ""})
    FloatingEmail = StringField('Email', validators=[DataRequired(), Length(min=2, max=20)], render_kw={"placeholder": ""}) # doesnt validate email, since the website doesnt need to use the email for anything yet, to simplify testing.
    FloatingPassword = PasswordField('Password', validators=[DataRequired(), Length(min=2, max=20)], render_kw={"placeholder": ""})
    FloatingConfirmPassword = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('FloatingPassword'), Length(min=2, max=20)], render_kw={"placeholder": ""})
    submit = SubmitField('Sign Up')
    fields = ("FloatingUsername", "FloatingEmail", "FloatingPassword", "FloatingConfirmPassword")

class LoginForm(FlaskForm):
    FloatingUsername = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)], render_kw={"placeholder": ""})
    FloatingPassword = PasswordField('Password', validators=[DataRequired(), Length(min=2, max=20)], render_kw={"placeholder": ""})
    # remember = BooleanField('Remember Me')
    submit = SubmitField('Log In')
    fields = ("FloatingUsername", "FloatingPassword")

# def validate_username(self, username):
#     if not username.data.isalnum():
#         raise ValidationError