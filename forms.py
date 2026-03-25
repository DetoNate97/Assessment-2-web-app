from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FileField, TextAreaField
from wtforms.validators import Length, EqualTo, InputRequired
from flask_wtf.file import FileAllowed, FileRequired

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
    worldnamefield = StringField('world_name')
    # characters:
    CharCreator = BooleanField('Character Creator', default="checked")
    # setting
    Historical = BooleanField('Historical Events and Folklore', render_kw={'disabled': "", 'class': 'indeterminate'})
    Maps = BooleanField('Maps', default="checked")
    Locations = BooleanField('Locations', render_kw={'disabled': "", 'class': 'indeterminate'})
    Hierarchy = BooleanField('Hierarchy System', render_kw={'disabled': "", 'class': 'indeterminate'})
    Factions = BooleanField('Factions and Aliances', render_kw={'disabled': "", 'class': 'indeterminate'})
    Laws = BooleanField('Laws', render_kw={'disabled': "", 'class': 'indeterminate', 'class': 'indeterminate'})
    Cultures = BooleanField('Cultures', render_kw={'disabled': "", 'class': 'indeterminate'})
    Technology = BooleanField('Technological Advancements', render_kw={'disabled': "", 'class': 'indeterminate'})
    Languages = BooleanField('Languages', render_kw={'disabled': "", 'class': 'indeterminate'})
    Currency = BooleanField('Currency System', render_kw={'disabled': "", 'class': 'indeterminate'})
    # gameplay
    Gameplay = BooleanField('Gameplay Mechanics', render_kw={'disabled': "", 'class': 'indeterminate'})
    Magic = BooleanField('Magic System', render_kw={'disabled': "", 'class': 'indeterminate'})
    Quests = BooleanField('Player Interactions and Quests', render_kw={'disabled': "", 'class': 'indeterminate'})

    submit = SubmitField('Create World')

    CharacterFields = ("CharCreator",)
    SettFields = ("Historical", "Maps", "Locations", "Hierarchy", "Factions", "Laws", "Cultures", "Technology", "Languages", "Currency")
    GameplayFields = ("Gameplay", "Magic", "Quests")
    fields = ("CharCreator", "Historical", "Maps", "Locations", "Hierarchy", "Factions", "Laws", "Cultures", "Technology", "Languages", "Currency", "Gameplay", "Magic", "Quests")
    # fields are split bc there are subheadings

class ChangeWorldNameForm(FlaskForm):
    worldnamefield = StringField('world_name', render_kw={"value": ""})
    submit = SubmitField('Change')

class CharForms(FlaskForm):
    CreateCharacterName = StringField('Character Name')
    CreateCharacterDescription = TextAreaField('Character Description')
    CreateCharacterBackstory = TextAreaField('Character Backstory')
    CharFields = ("CreateCharacterName", "CreateCharacterDescription", "CreateCharacterBackstory")
    submit_create = SubmitField('Create Character')

    HiddenCharName = StringField(render_kw={'style': 'display:none', 'value':'none'}) # for checking which character is being edited, since the name can be changed
    ChangeCharacterName = StringField('Character Name')
    ChangeCharacterDescription = TextAreaField('Character Description', default="")
    ChangeCharacterBackstory = TextAreaField('Character Backstory')
    submit_edit = SubmitField('Submit Changes')
    EditFields = ("ChangeCharacterName", "ChangeCharacterDescription", "ChangeCharacterBackstory")

class MapForm(FlaskForm):
    Map = FileField('Upload a map', validators=[FileAllowed(['jpg', 'png', 'webp', 'jpeg', 'jfif', 'avif', 'gif'], 'Please upload a valid image filetype')])
    submit = SubmitField('Upload')

class UploadForm(FlaskForm):
    file = FileField("Upload file", validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png', 'pdf'], "Only images or PDFs allowed")
    ])
    submit = SubmitField("Upload")
