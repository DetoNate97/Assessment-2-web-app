from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FileField, TextAreaField, SelectField, IntegerField
from wtforms.validators import Length, EqualTo, InputRequired, Optional
from flask_wtf.file import FileAllowed, FileRequired

class RegisterForm(FlaskForm):
    FloatingUsername = StringField('Username', validators=[InputRequired(), Length(min=2, max=20)], render_kw={"placeholder": ""})
    FloatingEmail = StringField('Email', validators=[InputRequired(), Length(min=2, max=20)], render_kw={"placeholder": ""}) # doesnt validate email, since the website doesnt need to use the email for anything yet this simplifies testing.
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
    Historical = BooleanField('Historical Events and Folklore', render_kw={'disabled': ""})
    Maps = BooleanField('Maps', default="checked")
    Locations = BooleanField('Locations')
    Hierarchy = BooleanField('Hierarchy System', render_kw={'disabled': ""})
    Factions = BooleanField('Factions and Aliances', render_kw={'disabled': ""})
    Laws = BooleanField('Laws', render_kw={'disabled': ""})
    Cultures = BooleanField('Cultures', render_kw={'disabled': ""})
    Technology = BooleanField('Technological Advancements', render_kw={'disabled': ""})
    Languages = BooleanField('Languages', render_kw={'disabled': ""})
    Currency = BooleanField('Currency System', render_kw={'disabled': ""})
    # gameplay
    Gameplay = BooleanField('Gameplay Mechanics', render_kw={'disabled': ""})
    Magic = BooleanField('Magic System', render_kw={'disabled': ""})
    Quests = BooleanField('Player Interactions and Quests', render_kw={'disabled': ""})

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
    ChangeCharacterDescription = TextAreaField('Character Description')
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

class LocForms(FlaskForm):
    CreateLocationName = StringField('Location Name')
    CreateLocationDescription = TextAreaField('Location Description')
    CreateLocationBackstory = TextAreaField('Location Backstory')
    LocFields = ("CreateLocationName", "CreateLocationDescription", "CreateLocationBackstory")
    submit_create = SubmitField('Create Location')

    HiddenLocName = StringField(render_kw={'style': 'display:none', 'value':'none'}) # for checking which character is being edited, since the name can be changed
    ChangeLocationName = StringField('Location Name')
    ChangeLocationDescription = TextAreaField('Location Description')
    ChangeLocationBackstory = TextAreaField('Location Backstory')
    submit_edit = SubmitField('Submit Changes')
    EditFields = ("ChangeLocationName", "ChangeLocationDescription", "ChangeLocationBackstory")

class HistForms(FlaskForm):
    CreateEventName = StringField('Event Name')
    CreateEventDescription = TextAreaField('Event Description')
    CreateEventBackstory = TextAreaField('Event Backstory')
    HistFields = ("CreateEventName", "CreateEventDescription", "CreateEventBackstory")
    submit_create = SubmitField('Create Event')

    HiddenEventName = StringField(render_kw={'style': 'display:none', 'value':'none'}) # for checking which character is being edited, since the name can be changed
    ChangeEventName = StringField('Event Name')
    ChangeEventDescription = TextAreaField('Event Description')
    ChangeEventBackstory = TextAreaField('Event Backstory')
    submit_edit = SubmitField('Submit Changes')
    EditFields = ("ChangeEventName", "ChangeEventDescription", "ChangeEventBackstory")

class FacForms(FlaskForm):
    CreateFactionName = StringField('Faction Name')
    CreateFactionDescription = TextAreaField('Faction Description')
    CreateFactionBackstory = TextAreaField('Faction Backstory')
    FacFields = ("CreateFactionName", "CreateFactionDescription", "CreateFactionBackstory")
    submit_create = SubmitField('Create Faction')

    HiddenFacName = StringField(render_kw={'style': 'display:none', 'value':'none'}) # for checking which character is being edited, since the name can be changed
    ChangeFactionName = StringField('Faction Name')
    ChangeFactionDescription = TextAreaField('Faction Description')
    ChangeFactionBackstory = TextAreaField('Faction Backstory')
    submit_edit = SubmitField('Submit Changes')
    EditFields = ("ChangeFactionName", "ChangeFactionDescription", "ChangeFactionBackstory")

class LawForms(FlaskForm):
    CreateLawName = StringField('Law Name')
    CreateLawDescription = TextAreaField('Law Description')
    CreateLawBackstory = TextAreaField('Law Backstory')
    LawFields = ("CreateLawName", "CreateLawDescription", "CreateLawBackstory")
    submit_create = SubmitField('Create Law')

    HiddenLawName = StringField(render_kw={'style': 'display:none', 'value':'none'}) # for checking which character is being edited, since the name can be changed
    ChangeLawName = StringField('Law Name')
    ChangeLawDescription = TextAreaField('Law Description')
    ChangeLawBackstory = TextAreaField('Law Backstory')
    submit_edit = SubmitField('Submit Changes')
    EditFields = ("ChangeLawName", "ChangeLawDescription", "ChangeLawBackstory")

class CulForms(FlaskForm):
    CreateCultureName = StringField('Culture Name')
    CreateCultureDescription = TextAreaField('Culture Description')
    CreateCultureBackstory = TextAreaField('Culture Backstory')
    CulFields = ("CreateCultureName", "CreateCultureDescription", "CreateCultureBackstory")
    submit_create = SubmitField('Create Culture')

    HiddenCulName = StringField(render_kw={'style': 'display:none', 'value':'none'}) # for checking which character is being edited, since the name can be changed
    ChangeCultureName = StringField('Culture Name')
    ChangeCultureDescription = TextAreaField('Culture Description')
    ChangeCultureBackstory = TextAreaField('Culture Backstory')
    submit_edit = SubmitField('Submit Changes')
    EditFields = ("ChangeCultureName", "ChangeCultureDescription", "ChangeCultureBackstory")

class TechForm(FlaskForm):
    CreateTechnology = TextAreaField('Description of technological level')
    submit_create = SubmitField('Save')

    EditTechnology = TextAreaField('Description of technological level')
    submit_edit = SubmitField('Save')

class LangForms(FlaskForm):
    CreateLanguageName = StringField('Language Name')
    CreateLanguageDescription = TextAreaField('Language Description')
    CreateLanguageBackstory = TextAreaField('Language Backstory')
    LangFields = ("CreateLanguageName", "CreateLanguageDescription", "CreateLanguageBackstory")
    submit_create = SubmitField('Create Language')

    HiddenLangName = StringField(render_kw={'style': 'display:none', 'value':'none'}) # for checking which character is being edited, since the name can be changed
    ChangeLanguageName = StringField('Language Name')
    ChangeLanguageDescription = TextAreaField('Language Description')
    ChangeLanguageBackstory = TextAreaField('Language Backstory')
    submit_edit = SubmitField('Submit Changes')
    EditFields = ("ChangeLanguageName", "ChangeLanguageDescription", "ChangeLanguageBackstory")

class MagForms(FlaskForm):
    CreateSpellName = StringField('Spell Name')
    CreateSpellDescription = TextAreaField('Spell Description')
    CreateSpellCost = StringField('Spell Cost')
    CreateSpellDamage = StringField('Spell Damage')
    MagFields = ("CreateSpellName", "CreateSpellDescription", "CreateSpellCost", "CreateSpellDamage")
    submit_create = SubmitField('Create Spell')

    HiddenSpellName = StringField(render_kw={'style': 'display:none', 'value':'none'}) # for checking which character is being edited, since the name can be changed
    ChangeSpellName = StringField('Spell Name')
    ChangeSpellDescription = TextAreaField('Spell Description')
    ChangeSpellCost = StringField('Spell Cost')
    ChangeSpellDamage = StringField('Spell Damage')
    submit_edit = SubmitField('Submit Changes')
    EditFields = ("ChangeSpellName", "ChangeSpellDescription", "ChangeSpellCost", "ChangeSpellDamage")

class QuestForms(FlaskForm):
    CreateQuestName = StringField('Quest Name')
    CreateQuestTask = TextAreaField('Quest Task')
    CreateQuestStart = SelectField('Quest Start NPC Name', choices=[])     # make these dropdowns that use the created characters
    CreateQuestFinish = SelectField('Quest Finish NPC Name', choices=[])   #
    CreateQuestReward = StringField('Quest Reward')
    QuestFields = ("CreateQuestName", "CreateQuestTask", "CreateQuestStart", "CreateQuestFinish", "CreateQuestReward")
    submit_create = SubmitField('Create Quest')

    HiddenQuestName = StringField(render_kw={'style': 'display:none', 'value':'none'}) # for checking which character is being edited, since the name can be changed
    ChangeQuestName = StringField('Quest Name')
    ChangeQuestTask = TextAreaField('Quest Task')
    ChangeQuestStart = SelectField('Quest Start NPC Name', choices=[])
    ChangeQuestFinish = SelectField('Quest Finish NPC Name', choices=[])
    ChangeQuestReward = StringField('Quest Reward')
    submit_edit = SubmitField('Submit Changes')
    EditFields = ("ChangeQuestName", "ChangeQuestTask", "ChangeQuestStart", "ChangeQuestFinish", "ChangeQuestReward")

class AccountForm(FlaskForm):
    Username = StringField('Username', validators=[Optional(), Length(min=2, max=20)])
    Email = StringField('Email', validators=[Optional(), Length(min=2, max=20)])
    CurrentPassword = PasswordField('Current Password', validators=[Optional()])
    NewPassword = PasswordField('New Password', validators=[EqualTo('ConfirmNewPassword', 'Passwords must match'), Optional(), Length(min=2, max=20)])
    ConfirmNewPassword = PasswordField('Confirm New Password', validators=[Optional(), EqualTo('NewPassword', 'Passwords must match'), Length(min=2, max=20)])
    submit = SubmitField("Confirm Changes")
    fields = ("Username", "Email", "CurrentPassword", "NewPassword", "ConfirmNewPassword")