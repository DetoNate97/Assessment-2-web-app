from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, InputRequired

class RegisterForm(FlaskForm):
    FloatingUsername = StringField('Username', validators=[InputRequired(), Length(min=2, max=20)], render_kw={"placeholder": ""})
    FloatingEmail = StringField('Email', validators=[InputRequired(), Length(min=2, max=20)], render_kw={"placeholder": ""}) # doesnt validate email, since the website doesnt need to use the email for anything yet, to simplify testing.
    Password = PasswordField('Password', validators=[InputRequired(), Length(min=2, max=20)], render_kw={"placeholder": ""})
    ConfirmPassword = PasswordField('Confirm Password', validators=[InputRequired(), EqualTo('Password'), Length(min=2, max=20)], render_kw={"placeholder": ""})
    submit = SubmitField('Sign Up')
    fields = ("FloatingUsername", "FloatingEmail", "Password", "ConfirmPassword")

class LoginForm(FlaskForm):
    FloatingUsername = StringField('Username', validators=[InputRequired(), Length(min=2, max=20)], render_kw={"placeholder": ""})
    FloatingPassword = PasswordField('Password', validators=[InputRequired(), Length(min=2, max=20)], render_kw={"placeholder": ""})
    # remember = BooleanField('Remember Me')
    submit = SubmitField('Log In')
    fields = ("FloatingUsername", "FloatingPassword")

class CustomSelectForm(FlaskForm):
    # add a name field.
    worldnamefield = StringField('world_name', render_kw={"placeholder": "New_world", "value": ""})
    # characters:
    CharCreator = BooleanField('Character Creator', default="checked")
    # setting
    Historical = BooleanField('Historical Events and Folklore', default="checked")
    Maps = BooleanField('Maps', default="checked")
    Locations = BooleanField('Locations', default="checked")
    Hierarchy = BooleanField('Hierarchy System', default="checked")
    Factions = BooleanField('Factions and Aliances', default="checked")
    Laws = BooleanField('Laws', default="checked")
    Cultures = BooleanField('Cultures', default="checked")
    Technology = BooleanField('Technological Advancements', default="checked")
    Languages = BooleanField('Languages', default="checked")
    Currency = BooleanField('Currency System', default="checked")
    # gameplay
    Gameplay = BooleanField('Gameplay Mechanics', default="checked")
    Magic = BooleanField('Magic System', default="checked")
    Quests = BooleanField('Player Interactions and Quests', default="checked")

    submit = SubmitField('Create World')

    CharacterFields = ("CharCreator",)
    SettFields = ("Historical", "Maps", "Locations", "Hierarchy", "Factions", "Laws", "Cultures", "Technology", "Languages", "Currency")
    GameplayFields = ("Gameplay", "Magic", "Quests")
    fields = ("CharCreator", "Historical", "Maps", "Locations", "Hierarchy", "Factions", "Laws", "Cultures", "Technology", "Languages", "Currency", "Gameplay", "Magic", "Quests")
    # fields are split bc there are subheadings

class ChangeWorldNameForm(FlaskForm):
    worldnamefield = StringField('world_name', render_kw={"placeholder": "{{world_name}}", "value": ""})
    submit = SubmitField('Change')


# def validate_username(self, username):
#     if not username.data.isalnum():
#         raise ValidationError