from flask import Flask, render_template, url_for, redirect, flash, session
from flask_login import login_user, logout_user # not used, but remember to use next time i need to make a login system
from forms import RegisterForm, LoginForm, CustomSelectForm, ChangeWorldNameForm, CharForms, MapForm, AccountForm, LocForms, HistForms, FacForms, LawForms, CulForms, TechForms, LangForms, CurrForms, MagForms, QuestForms
import os, sqlite3, secrets, json, time
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# alternate security modules: import hashlib, zlib
# print(hashlib.algorithms_available)
# output = hashlib.sha256(input.encode()).hexdigest()

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['MAPS_FOLDER'] = os.path.join("static", "maps")  

# database file path:
db_path = os.path.join("database", "database.db")
# change path to fit venv location

# connect to the database:
try:
    DB = sqlite3.connect(db_path, check_same_thread=False) # "check_same_thread=False" fix used from assessment 1.
    print(f" * Connected to database")
except sqlite3.OperationalError as error:
    print(f"Error: {error}")
    exit()

# website routes:
@app.route('/')
def welcome():
    '''
    Handles rendering of the landing page of the website. its the page the viewer first sees.
    Returns a rendered html. no methods :)
    '''
    return render_template('welcome.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    '''
    Handles the user login page.
    
    Methods:
    GET: render the login.html with the form.
    POST: validate the submitted data, gets the stored password with the username:
            if the password returns a none type: flash an error message
            if the password exists:
                if the password matches: logs in the user
                if the password doesnt match: flash an error message
    '''
    form = LoginForm()
    fields = form.fields
    page = "Log In"

    if form.validate_on_submit():
        # get submitted data:
        log_user, log_pass = str(form.FloatingUsername.data), str(form.FloatingPassword.data) 
        # get stored password:
        db_data = DB.execute("SELECT password FROM Users WHERE username = ?", [log_user]).fetchall() # db_data is in the format [("password",)]. why, sql, why.
        # check if there is a stored password:
        if not db_data: 
            flash(f'Failed to log in, user {log_user} does not exist', 'danger')
        else: 
            password_hash = db_data[0][0] # gets the data out of the stupid double tuple trouble.
            # compare input and stored passwords:
            if check_password_hash(password_hash, log_pass):
                flash(f'Successfully logged in user {log_user}!', 'success')    
                session['current_user'] = log_user
                session['user_worlds'] = os.path.join("database", f"{log_user}_worlds.ndjson")
                return redirect(url_for('home'))
            else:
                flash(f'failed to log in, check username and password.', 'danger')
    return render_template('login.html', page=page, form=form, fields=fields)

@app.route('/register', methods=['GET', 'POST'])
def register():
    '''
    Handles the user registration page.

    Methods: 
    GET: render the register.html with the form.
    POST: validate the submitted data, checks if the user already exists:
          if the username isnt taken: saves the user to the database, logs in the user, and redirects to the home page.
          if the username is taken: flash an error message.
    '''
    page = "Register"
    form = RegisterForm()
    fields = form.fields

    if form.validate_on_submit():
        # get submitted data:
        reg_user, reg_email, reg_pass = str(form.FloatingUsername.data), str(form.FloatingEmail.data), str(form.Password.data)
        # check if the username is already taken:
        if not DB.execute( f"SELECT password FROM Users WHERE username = ?", [reg_user] ).fetchall():
            # save new user to the database:
            cursor = DB.cursor()
            cursor.execute("INSERT INTO Users (username, email, password) VALUES (?, ?, ?)", (reg_user, reg_email, f"{generate_password_hash(reg_pass)}"))
            DB.commit()
            session['current_user'] = reg_user
            # set the path for the user's stored worlds:
            session['user_worlds'] = os.path.join("database", f"{reg_user}_worlds.ndjson")
            flash(f'Account created for {form.FloatingUsername.data}!', 'success')
            return redirect(url_for('home'))
        else:
            flash(f'Failed to create account: account name already exists.', 'danger')
    return render_template('register.html', page=page, form=form, fields=fields)

@app.route('/home', methods=['GET', 'POST'])
def home():
    '''
    Handles the home page. this is where all the cards for the user's worlds are displayed. slightly inspired by google docs

    Methods: 
    GET: render the home.html with the form in the modal.
    POST: validate the submitted data, create a new world with the selected modules.
    '''
    form = CustomSelectForm()
    worldnamefield = form.worldnamefield
    CharFields = form.CharacterFields
    SettFields = form.SettFields
    GameFields = form.GameplayFields # fields are split bc there are subheadings
    fields = form.fields
    current_user = session.get('current_user')
    user_worlds = session.get('user_worlds')
    page = "home"
    data = []

    filetypes = ['jpg', 'png', 'webp', 'jpeg', 'jfif', 'avif', 'gif'] # valid filetypes for map uploads.
    session['filetypes'] = filetypes

    # attempt to open the stored worlds. if there is no file it means there are no stored worlds.
    try:
        with open(user_worlds, "r") as file:
            for line in file:
                data.append(json.loads(line))
    except:
        pass

    # redirect to login if there is no user logged in: (this prevents a crash when saving the py files)
    if not current_user:
        return redirect(url_for("login"))
    if form.validate_on_submit():
        if not form.worldnamefield.data:
            world_name = "New_World"
            check = False
            world_num = 0
            if data:
                for world in data:
                    if world["name"] == "New_World":
                        check=False
                    
                while check != True:
                    for world in data:
                        if world["name"] == world_name:
                            world_num += 1
                            world_name = f"New_World_{world_num}"
                        else:
                            check=True
            else:
                check = True
        else:
            if data:
                for world in data:
                    if form.worldnamefield.data != world["name"]:
                        pass
                    else:
                        flash('name already exists', 'danger')
                        return redirect(url_for("home"))
            world_name = form.worldnamefield.data
        # record the selected modules:
        modules = []
        for i in form.fields:
            if form[i].data:
                modules.append(i)
        session['world_modules'] = modules
        # create the world in the json file:
        data = {
            "name": world_name, 
            "modules": modules,
            }
        if "CharCreator" in modules:
            data["characters"] = {}
        if "Locations" in modules:
            data["locations"] = {}
        if "Historical" in modules:
            data["history"] = {}
        if "Factions" in modules:
            data["factions"] = {}
        if "Laws" in modules:
            data["laws"] = {}
        if "Cultures" in modules:
            data["cultures"] = {}
        if "Technology" in modules:
            data["technology"] = {"":["",""]}
        if "Languages" in modules:
            data["languages"] = {}
        if "Currency" in modules:
            data["currency"] = {"":["","","","10:1"]}
        if "Magic" in modules:
            data["magic"] = {}
        if "Quests" in modules:
            data["quests"] = {}
        with open(user_worlds, "a") as file:
            file.write(json.dumps(data) + "\n")
        return redirect(url_for('world', world_name=world_name))
    return render_template('home.html', page=page, user=current_user, form=form, fields=fields, worldnamefield=worldnamefield, CharFields=CharFields, SettFields=SettFields, GameFields=GameFields, data=data)    

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    '''
    Handles rendering of the settings page. slightly inspired by microsoft edge settings

    methods
    '''
    form = AccountForm()
    fields = form.fields
    page = "settings"
    current_user = session.get('current_user')
    if not current_user:
        return redirect(url_for("login"))
    db_data = DB.execute( f"SELECT password FROM Users WHERE username = ?", [current_user] ).fetchall()
    password_hash = db_data[0][0]
    email = (DB.execute( f"SELECT email FROM Users WHERE username = ?", [current_user] ).fetchall())[0][0]
    default = {"Username": current_user, "Email": email}
    if form.validate_on_submit():
        if form.Username.data:
            current_user = session.get('current_user')

            data = []
            filetypes = session.get('filetypes')
            user_worlds = session.get('user_worlds')
            try:
                with open(user_worlds, "r") as file:
                    for line in file:
                        data.append(json.loads(line))
            except:
                pass
            for i in data:
                world_name = i["name"]
                for type in filetypes:
                    file = os.path.join(app.config['MAPS_FOLDER'], f"{current_user}_{world_name}_map.{type}")
                    if os.path.exists(file):
                        os.rename(file, os.path.join(app.config['MAPS_FOLDER'], f"{form.Username.data}_{world_name}_map.{type}"))
            
            file=os.path.join("database", f"{current_user}_worlds.ndjson")
            if os.path.exists(file):
                os.rename(file, os.path.join("database", f"{form.Username.data}_worlds.ndjson"))

            cursor = DB.cursor()
            cursor.execute("UPDATE Users SET username=? WHERE username=?", [form.Username.data, current_user])
            DB.commit()
            session['current_user'] = form.Username.data

        if form.Email.data:
            cursor = DB.cursor()
            cursor.execute("UPDATE Users SET email=? WHERE username=?", [form.Email.data, current_user])
            DB.commit()
        if form.NewPassword.data:
            if check_password_hash(password_hash, form.CurrentPassword.data):
                hash_password = generate_password_hash(form.NewPassword.data)
                cursor = DB.cursor()
                cursor.execute("UPDATE Users SET password=? WHERE username=?", [hash_password, current_user])
                DB.commit()
                pass
            else:
                flash("password does not match current password", "danger")
        current_user = session.get('current_user')
        email = (DB.execute( f"SELECT email FROM Users WHERE username = ?", [current_user] ).fetchall())[0][0]
        default = {"Username": current_user, "Email": email}
        flash('updated details', 'success')
    return render_template('settings.html', page=page, form=form, fields=fields, default=default)

@app.route('/open_world/<world_name>', methods=['POST'])
def open_world(world_name):
    '''
    redirects to the world. 
    gets the world name, finds the world in the json, records the modules, redirects to the world

    parameters:
    world_name: the name of the world... can it get any more obvious?

    returns:
    a redirect to the world
    '''
    world_name = world_name
    data = []
    user_worlds = session.get('user_worlds')
    try:
        with open(user_worlds, "r") as file:
            for line in file:
                data.append(json.loads(line))
    except:
        pass
    for i in data:
        if i["name"] == world_name:
            modules = i["modules"]
            pass # for some reason pass works here but the one to change name needs break
    session['world_modules'] = modules
    session['world_name'] = world_name
    return redirect(url_for('world', world_name=world_name))

@app.route('/create_new_book', methods=['POST'])
def create_new_book():
    '''
    redirects to the world. similar to the open_world function, but instead of opening the modal to select modules, they are preselected.
    creates the world in the json with pre-set modules and redirects to it.

    returns:
    a redirect to the world
    '''
    user_worlds = session.get('user_worlds')
    modules = ['CharCreator', 'Historical', 'Maps', 'Locations', 'Factions', 'Laws', 'Cultures', 'Technology', 'Languages', 'Currency'] # set the preset modules
    session['world_modules'] = modules
    world_name = "New_Book"
    data = {"name": world_name, "modules": modules}
    data["characters"] = {}
    if "CharCreator" in modules:
        data["characters"] = {}
    if "Locations" in modules:
        data["locations"] = {}
    if "Historical" in modules:
        data["history"] = {}
    if "Factions" in modules:
        data["factions"] = {}
    if "Laws" in modules:
        data["laws"] = {}
    if "Cultures" in modules:
        data["cultures"] = {}
    if "Technology" in modules:
        data["technology"] = {"":["",""]}
    if "Languages" in modules:
        data["languages"] = {}
    if "Currency" in modules:
        data["currency"] = {"":["","","","10:1"]}
    if "Magic" in modules:
        data["magic"] = {}
    if "Quests" in modules:
        data["quests"] = {}
    with open(user_worlds, "a") as file:
        file.write(json.dumps(data) + "\n")
    return redirect(url_for('world', world_name=world_name))

@app.route('/create_new_movie', methods=['POST'])
def create_new_movie():
    '''
    redirects to the world. similar to the open_world function, but instead of opening the modal to select modules, they are preselected.
    creates the world in the json with pre-set modules and redirects to it.

    returns:
    a redirect to the world
    '''
    user_worlds = session.get('user_worlds')
    modules = ['CharCreator', 'Historical', 'Maps', 'Locations', 'Factions', 'Laws', 'Cultures', 'Technology', 'Languages', 'Currency'] # set the preset modules
    session['world_modules'] = modules
    world_name = "New_Movie"
    data = {"name": world_name, "modules": modules}
    data["characters"] = {}
    if "CharCreator" in modules:
        data["characters"] = {}
    if "Locations" in modules:
        data["locations"] = {}
    if "Historical" in modules:
        data["history"] = {}
    if "Factions" in modules:
        data["factions"] = {}
    if "Laws" in modules:
        data["laws"] = {}
    if "Cultures" in modules:
        data["cultures"] = {}
    if "Technology" in modules:
        data["technology"] = {"":["",""]}
    if "Languages" in modules:
        data["languages"] = {}
    if "Currency" in modules:
        data["currency"] = {"":["","","","10:1"]}
    if "Magic" in modules:
        data["magic"] = {}
    if "Quests" in modules:
        data["quests"] = {}

    with open(user_worlds, "a") as file:
        file.write(json.dumps(data) + "\n")
    return redirect(url_for('world', world_name=world_name))


@app.route('/create_new_game', methods=['POST'])
def create_new_game():
    '''
    redirects to the world. similar to the open_world function, but instead of opening the modal to select modules, they are preselected.
    creates the world in the json with pre-set modules and redirects to it.

    returns:
    a redirect to the world
    '''
    user_worlds = session.get('user_worlds')
    modules = ["CharCreator", "Historical", "Maps", "Locations", "Factions", "Laws", "Cultures", "Technology", "Languages", "Currency", "Magic", "Quests"] # set the preset modules
    session['world_modules'] = modules
    world_name = "New_Game"
    data = {"name": world_name, "modules": modules}
    data["characters"] = {}
    if "CharCreator" in modules:
        data["characters"] = {}
    if "Locations" in modules:
        data["locations"] = {}
    if "Historical" in modules:
        data["history"] = {}
    if "Factions" in modules:
        data["factions"] = {}
    if "Laws" in modules:
        data["laws"] = {}
    if "Cultures" in modules:
        data["cultures"] = {}
    if "Technology" in modules:
        data["technology"] = {"":["",""]}
    if "Languages" in modules:
        data["languages"] = {}
    if "Currency" in modules:
        data["currency"] = {"":["","","","10:1"]}
    if "Magic" in modules:
        data["magic"] = {}
    if "Quests" in modules:
        data["quests"] = {}
    with open(user_worlds, "a") as file:
        file.write(json.dumps(data) + "\n")
    return redirect(url_for('world', world_name=world_name))

@app.route(f'/world/<world_name>', methods=['GET', 'POST'])
def world(world_name):
    '''
    Handles the custom worlds.
    instead of somehow creating an individual html file for each world, this instead is a single file that gets all the data for the world and displays it.

    parameters:
    world name: the name of the world. also used for files related 

    returns:
    a rendered html
    '''
    modules = session.get('world_modules')
    current_user = session.get('current_user')
    user_worlds = session.get('user_worlds')
    data = []
    form = ChangeWorldNameForm()
    Charforms = CharForms()
    Locforms = LocForms()
    Histforms = HistForms()
    Facforms = FacForms()
    Lawforms = LawForms()
    Culforms = CulForms()
    Techforms = TechForms()
    Langforms = LangForms()
    Currforms = CurrForms()
    Magforms = MagForms()
    Questforms = QuestForms()
    Mapform = MapForm()
    charfields = Charforms.CharFields
    chareditfields = Charforms.EditFields
    locfields = Locforms.LocFields
    loceditfields = Locforms.EditFields
    histfields = Histforms.HistFields
    histeditfields = Histforms.EditFields
    facfields = Facforms.FacFields
    faceditfields = Facforms.EditFields
    lawfields = Lawforms.LawFields
    laweditfields = Lawforms.EditFields
    culfields = Culforms.CulFields
    culeditfields = Culforms.EditFields
    techfields = Techforms.TechFields
    techeditfields = Techforms.EditFields
    langfields = Langforms.LangFields
    langeditfields = Langforms.EditFields
    currfields = Currforms.CurrFields
    curreditfields = Currforms.EditFields
    magfields = Magforms.MagFields
    mageditfields = Magforms.EditFields
    questfields = Questforms.QuestFields
    questeditfields = Questforms.EditFields
    
    # checks the filetype of the currently saved map
    ext = ""
    filetypes = ['jpg', 'png', 'webp', 'jpeg', 'jfif', 'avif', 'gif'] # valid filetypes for map uploads. i should just make this a const like DB
    session['filetypes'] = filetypes
    for type in filetypes:
        if os.path.exists(os.path.join(app.config['MAPS_FOLDER'], f"{current_user}_{world_name}_map.{type}")):
            ext = type
    session['ext'] = ext

    # redirect to login if there is no user logged in: (this prevents a crash when saving the py files)
    if not current_user:
        return redirect(url_for("login"))
    # get the characters from the json
    characters = []
    if "CharCreator" in modules:
        with open(user_worlds, "r") as file:
            for line in file:
                world = json.loads(line)
                data.append(world)
        for i in data:
            if i["name"] == world_name:
                characters = i["characters"]
        data = []
    
    # gets the characters and sets them as the options for the quest module.
    questoptions = ["",]
    for char in characters:
        questoptions.append(char)
    Questforms.CreateQuestStart.choices = [(o, o) for o in questoptions]
    Questforms.CreateQuestFinish.choices = [(o, o) for o in questoptions]
    Questforms.ChangeQuestStart.choices = [(o, o) for o in questoptions]
    Questforms.ChangeQuestFinish.choices = [(o, o) for o in questoptions]

    locations = []
    if "Locations" in modules:
        with open(user_worlds, "r") as file:
            for line in file:
                world = json.loads(line)
                data.append(world)
        for i in data:
            if i["name"] == world_name:
                locations = i["locations"]
        data = []

    events = []
    if "Historical" in modules:
        with open(user_worlds, "r") as file:
            for line in file:
                world = json.loads(line)
                data.append(world)
        for i in data:
            if i["name"] == world_name:
                events = i["history"]
        data = []

    factions = []
    if "Factions" in modules:
        with open(user_worlds, "r") as file:
            for line in file:
                world = json.loads(line)
                data.append(world)
        for i in data:
            if i["name"] == world_name:
                factions = i["factions"]
        data = []

    laws = []
    if "Laws" in modules:
        with open(user_worlds, "r") as file:
            for line in file:
                world = json.loads(line)
                data.append(world)
        for i in data:
            if i["name"] == world_name:
                laws = i["laws"]
        data = []

    cultures = []
    if "Cultures" in modules:
        with open(user_worlds, "r") as file:
            for line in file:
                world = json.loads(line)
                data.append(world)
        for i in data:
            if i["name"] == world_name:
                cultures = i["cultures"]
        data = []

    technology = []
    if "Technology" in modules:
        with open(user_worlds, "r") as file:
            for line in file:
                world = json.loads(line)
                data.append(world)
        for i in data:
            if i["name"] == world_name:
                technology = i["technology"]
        data = []
    
    languages = []
    if "Languages" in modules:
        with open(user_worlds, "r") as file:
            for line in file:
                world = json.loads(line)
                data.append(world)
        for i in data:
            if i["name"] == world_name:
                languages = i["languages"]
        data = []

    currencies = []
    if "Currency" in modules:
        with open(user_worlds, "r") as file:
            for line in file:
                world = json.loads(line)
                data.append(world)
        for i in data:
            if i["name"] == world_name:
                currencies = i["currency"]
        data = []


    spells = []
    if "Magic" in modules:
        with open(user_worlds, "r") as file:
            for line in file:
                world = json.loads(line)
                data.append(world)
        for i in data:
            if i["name"] == world_name:
                spells = i["magic"]
        data = []

    quests = []
    if "Quests" in modules:
        with open(user_worlds, "r") as file:
            for line in file:
                world = json.loads(line)
                data.append(world)
        for i in data:
            if i["name"] == world_name:
                quests = i["quests"]
        data = []
    
    # if the form is submitted, check which fields have been filled
    if form.validate_on_submit():
        # since there are many forms on this one page, it needs to check which one was filled and submitted

        #
        # set all the fields to a variable for easy checking
        #
        charname = Charforms.CreateCharacterName.data
        chardesc = Charforms.CreateCharacterDescription.data
        charback = Charforms.CreateCharacterBackstory.data
        editcharname = Charforms.ChangeCharacterName.data
        editchardesc = Charforms.ChangeCharacterDescription.data
        editcharback = Charforms.ChangeCharacterBackstory.data

        locname = Locforms.CreateLocationName.data
        locfac = Locforms.CreateLocationFaction.data
        loceco = Locforms.CreateLocationEconomy.data
        loccul = Locforms.CreateLocationCultures.data
        loclang = Locforms.CreateLocationLanguages.data
        locgov = Locforms.CreateLocationGovernment.data
        editlocname = Locforms.ChangeLocationName.data
        editlocfac = Locforms.ChangeLocationFaction.data
        editloceco = Locforms.ChangeLocationEconomy.data
        editloccul = Locforms.ChangeLocationCultures.data
        editloclang = Locforms.ChangeLocationLanguages.data
        editlocgov = Locforms.ChangeLocationGovernment.data

        eventname = Histforms.CreateEventName.data
        eventdesc = Histforms.CreateEventDescription.data
        eventback = Histforms.CreateEventBackstory.data
        editeventname = Histforms.ChangeEventName.data
        editeventdesc = Histforms.ChangeEventDescription.data
        editeventback = Histforms.ChangeEventBackstory.data

        facname = Facforms.CreateFactionName.data
        facdesc = Facforms.CreateFactionDescription.data
        facback = Facforms.CreateFactionBackstory.data
        editfacname = Facforms.ChangeFactionName.data
        editfacdesc = Facforms.ChangeFactionDescription.data
        editfacback = Facforms.ChangeFactionBackstory.data

        lawname = Lawforms.CreateLawName.data
        lawdesc = Lawforms.CreateLawDescription.data
        lawback = Lawforms.CreateLawBackstory.data
        editlawname = Lawforms.ChangeLawName.data
        editlawdesc = Lawforms.ChangeLawDescription.data
        editlawback = Lawforms.ChangeLawBackstory.data
        
        culname = Culforms.CreateCultureName.data
        culdesc = Culforms.CreateCultureDescription.data
        culback = Culforms.CreateCultureBackstory.data
        editculname = Culforms.ChangeCultureName.data
        editculdesc = Culforms.ChangeCultureDescription.data
        editculback = Culforms.ChangeCultureBackstory.data

        techname = Techforms.CreateTechnologyName.data
        techdesc = Techforms.CreateTechnologyDescription.data
        techback = Techforms.CreateTechnologyBackstory.data
        edittechname = Techforms.ChangeTechnologyName.data
        edittechdesc = Techforms.ChangeTechnologyDescription.data
        edittechback = Techforms.ChangeTechnologyBackstory.data

        langname = Langforms.CreateLanguageName.data
        langdesc = Langforms.CreateLanguageDescription.data
        langback = Langforms.CreateLanguageBackstory.data
        editlangname = Langforms.ChangeLanguageName.data
        editlangdesc = Langforms.ChangeLanguageDescription.data
        editlangback = Langforms.ChangeLanguageBackstory.data

        currplat = Currforms.CreateCurrencyPlatinum.data
        currgold = Currforms.CreateCurrencyGold.data
        currsilv = Currforms.CreateCurrencySilver.data
        currcopp = Currforms.CreateCurrencyCopper.data
        currconv = Currforms.CreateConversionRatio.data
        editcurrplat = Currforms.ChangeCurrencyPlatinum.data
        editcurrgold = Currforms.ChangeCurrencyGold.data
        editcurrsilv = Currforms.ChangeCurrencySilver.data
        editcurrcopp = Currforms.ChangeCurrencyCopper.data
        editcurrconv = Currforms.ChangeConversionRatio.data
        
        spellname = Magforms.CreateSpellName.data
        spelldesc = Magforms.CreateSpellDescription.data
        spellcost = Magforms.CreateSpellCost.data
        spelldmg = Magforms.CreateSpellDamage.data
        editspellname = Magforms.ChangeSpellName.data
        editspelldesc = Magforms.ChangeSpellDescription.data
        editspellcost = Magforms.ChangeSpellCost.data
        editspelldmg = Magforms.ChangeSpellDamage.data

        questname = Questforms.CreateQuestName.data
        questtask = Questforms.CreateQuestTask.data
        queststart = Questforms.CreateQuestStart.data
        questfinish = Questforms.CreateQuestFinish.data
        questreward = Questforms.CreateQuestReward.data
        editquestname = Questforms.ChangeQuestName.data
        editquesttask = Questforms.ChangeQuestTask.data
        editqueststart = Questforms.ChangeQuestStart.data
        editquestfinish = Questforms.ChangeQuestFinish.data
        editquestreward = Questforms.ChangeQuestReward.data
        
        #
        # check if the world name field was filled
        #
        if form.worldnamefield.data:

            with open(user_worlds, "r") as file:
                for line in file:
                    world = json.loads(line)
                    data.append(world)
            # check if a world already has that name
            for i in data:
                if i['name'] == form.worldnamefield.data:
                    flash('cannot rename world, a world already has that name', 'danger')
                    return redirect(url_for('world', world_name = world_name))
            for i in data:
                if i["name"] == world_name:
                    i["name"] = form.worldnamefield.data
                    break # makes sure only 1 world gets changed
            # write the edited version back into json
            with open(user_worlds, 'w') as file:
                for obj in data:
                    file.write(json.dumps(obj) + "\n")

            ext = session.get('ext')
            current_user = session.get('current_user')
            file = ""
            if ext:
                file = os.path.join(app.config['MAPS_FOLDER'], f"{current_user}_{world_name}_map.{ext}")
            if file:
                os.rename(file, os.path.join(app.config['MAPS_FOLDER'], f"{current_user}_{form.worldnamefield.data}_map.{ext}"))

            return redirect(url_for("world", world_name=form.worldnamefield.data))

        if charname or chardesc or charback:
            if charname and chardesc and charback:
                data = []
                with open(user_worlds, "r") as file:
                    for line in file:
                        world = json.loads(line)
                        data.append(world)
                for i in data:
                    if i["name"] == world_name:
                        i["characters"][charname] = [chardesc, charback]
                with open(user_worlds, 'w') as file:
                    for obj in data:
                        file.write(json.dumps(obj) + "\n")
                return redirect(url_for("world", world_name=world_name))
            else:
                flash('make sure all fields are filled', 'danger')
                return redirect(url_for("world", world_name=world_name))

        if editcharname or editchardesc or editcharback:
            if editcharname and editchardesc and editcharback:
                data = []
                with open(user_worlds, "r") as file:
                    for line in file:
                        world = json.loads(line)
                        data.append(world)
                for i in data:
                    if i["name"] == world_name:
                        for char in i['characters']:
                            if char == Charforms.HiddenCharName.data:
                                i['characters'][char] = [editchardesc, editcharback]
                                i['characters'][editcharname] = i['characters'].pop(char)

                with open(user_worlds, 'w') as file:
                    for obj in data:
                        file.write(json.dumps(obj) + "\n")
                return redirect(url_for("world", world_name=world_name))
            else:
                flash('make sure all fields are filled', 'danger')
                return redirect(url_for("world", world_name=world_name))
            
        if locname or locfac or loceco or loccul or loclang or locgov:
            if locname and locfac and loceco and loccul and loclang and locgov:
                data = []
                with open(user_worlds, "r") as file:
                    for line in file:
                        world = json.loads(line)
                        data.append(world)
                for i in data:
                    if i["name"] == world_name:
                        i["locations"][locname] = [locfac, loceco, loccul, loclang, locgov]
                with open(user_worlds, 'w') as file:
                    for obj in data:
                        file.write(json.dumps(obj) + "\n")
                return redirect(url_for("world", world_name=world_name))
            else:
                flash('make sure all fields are filled', 'danger')
                return redirect(url_for("world", world_name=world_name))
            
        if editlocname or editlocfac or editloceco or editloccul or editloclang or editlocgov:
            if editlocname and editlocfac and editloceco and editloccul and editloclang and editlocgov:
                data = []
                with open(user_worlds, "r") as file:
                    for line in file:
                        world = json.loads(line)
                        data.append(world)
                for i in data:
                    if i["name"] == world_name:
                        for loc in i['locations']:
                            if loc == Locforms.HiddenLocName.data:
                                i['locations'][loc] = [editlocfac, editloceco, editloccul, editloclang, editlocgov]
                                i['locations'][editlocname] = i['locations'].pop(loc)

                with open(user_worlds, 'w') as file:
                    for obj in data:
                        file.write(json.dumps(obj) + "\n")
                return redirect(url_for("world", world_name=world_name))
            else:
                flash('make sure all fields are filled', 'danger')
                return redirect(url_for("world", world_name=world_name))
            
        if eventname or eventdesc or eventback:
            if eventname and eventdesc and eventback:
                data = []
                with open(user_worlds, "r") as file:
                    for line in file:
                        world = json.loads(line)
                        data.append(world)
                for i in data:
                    if i["name"] == world_name:
                        i["history"][eventname] = [eventdesc, eventback]
                with open(user_worlds, 'w') as file:
                    for obj in data:
                        file.write(json.dumps(obj) + "\n")
                return redirect(url_for("world", world_name=world_name))
            else:
                flash('make sure all fields are filled', 'danger')
                return redirect(url_for("world", world_name=world_name))
            
        if editeventname or editeventdesc or editeventback:
            if editeventname and editeventdesc and editeventback:
                data = []
                with open(user_worlds, "r") as file:
                    for line in file:
                        world = json.loads(line)
                        data.append(world)
                for i in data:
                    if i["name"] == world_name:
                        for event in i['history']:
                            if event == Histforms.HiddenEventName.data:
                                i['history'][event] = [editeventdesc, editeventback]
                                i['history'][editeventname] = i['history'].pop(event)

                with open(user_worlds, 'w') as file:
                    for obj in data:
                        file.write(json.dumps(obj) + "\n")
                return redirect(url_for("world", world_name=world_name))
            else:
                flash('make sure all fields are filled', 'danger')
                return redirect(url_for("world", world_name=world_name))
            
        if facname or facdesc or facback:
            if facname and facdesc and facback:
                data = []
                with open(user_worlds, "r") as file:
                    for line in file:
                        world = json.loads(line)
                        data.append(world)
                for i in data:
                    if i["name"] == world_name:
                        i["factions"][facname] = [facdesc, facback]
                with open(user_worlds, 'w') as file:
                    for obj in data:
                        file.write(json.dumps(obj) + "\n")
                return redirect(url_for("world", world_name=world_name))
            else:
                flash('make sure all fields are filled', 'danger')
                return redirect(url_for("world", world_name=world_name))
            
        if editfacname or editfacdesc or editfacback:
            if editfacname and editfacdesc and editfacback:
                data = []
                with open(user_worlds, "r") as file:
                    for line in file:
                        world = json.loads(line)
                        data.append(world)
                for i in data:
                    if i["name"] == world_name:
                        for fac in i['factions']:
                            if fac == Facforms.HiddenFacName.data:
                                i['factions'][fac] = [editfacdesc, editfacback]
                with open(user_worlds, 'w') as file:
                    for obj in data:
                        file.write(json.dumps(obj) + "\n")
                return redirect(url_for("world", world_name=world_name))
            else:
                flash('make sure all fields are filled', 'danger')
                return redirect(url_for("world", world_name=world_name))
        
        if lawname or lawdesc or lawback:
            if lawname and lawdesc and lawback:
                data = []
                with open(user_worlds, "r") as file:
                    for line in file:
                        world = json.loads(line)
                        data.append(world)
                for i in data:
                    if i["name"] == world_name:
                        i["laws"][lawname] = [lawdesc, lawback]
                with open(user_worlds, 'w') as file:
                    for obj in data:
                        file.write(json.dumps(obj) + "\n")
                return redirect(url_for("world", world_name=world_name))
            else:
                flash('make sure all fields are filled', 'danger')
                return redirect(url_for("world", world_name=world_name))
            
        if editlawname or editlawdesc or editlawback:
            if editlawname and editlawdesc and editlawback:
                data = []
                with open(user_worlds, "r") as file:
                    for line in file:
                        world = json.loads(line)
                        data.append(world)
                for i in data:
                    if i["name"] == world_name:
                        for law in i['laws']:
                            if law == Lawforms.HiddenLawName.data:
                                i['laws'][law] = [editlawdesc, editlawback]
                with open(user_worlds, 'w') as file:
                    for obj in data:
                        file.write(json.dumps(obj) + "\n")
                return redirect(url_for("world", world_name=world_name))
            else:
                flash('make sure all fields are filled', 'danger')
                return redirect(url_for("world", world_name=world_name))
            
        if culname or culdesc or culback:
            if culname and culdesc and culback:
                data = []
                with open(user_worlds, "r") as file:
                    for line in file:
                        world = json.loads(line)
                        data.append(world)
                for i in data:
                    if i["name"] == world_name:
                        i["cultures"][culname] = [culdesc, culback]
                with open(user_worlds, 'w') as file:
                    for obj in data:
                        file.write(json.dumps(obj) + "\n")
                return redirect(url_for("world", world_name=world_name))
            else:
                flash('make sure all fields are filled', 'danger')
                return redirect(url_for("world", world_name=world_name))
            
        if editculname or editculdesc or editculback:
            if editculname and editculdesc and editculback:
                data = []
                with open(user_worlds, "r") as file:
                    for line in file:
                        world = json.loads(line)
                        data.append(world)
                for i in data:
                    if i["name"] == world_name:
                        for cul in i['cultures']:
                            if cul == Culforms.HiddenCulName.data:
                                i['cultures'][cul] = [editculdesc, editculback]
                with open(user_worlds, 'w') as file:
                    for obj in data:
                        file.write(json.dumps(obj) + "\n")
                return redirect(url_for("world", world_name=world_name))
            else:
                flash('make sure all fields are filled', 'danger')
                return redirect(url_for("world", world_name=world_name))
            
        if edittechdesc:
            data = []
            with open(user_worlds, "r") as file:
                for line in file:
                    world = json.loads(line)
                    data.append(world)
            for i in data:
                if i["name"] == world_name:
                    for tech in i['technology']:
                        if tech == Techforms.HiddenTechName.data:
                            i['technology'][tech] = [edittechdesc, edittechback]
                            i['technology'][edittechname] = i['technology'].pop(tech)
                            break
            with open(user_worlds, 'w') as file:
                for obj in data:
                    file.write(json.dumps(obj) + "\n")
            return redirect(url_for("world", world_name=world_name))
            
        if langname or langdesc or langback:
            if langname and langdesc and langback:
                data = []
                with open(user_worlds, "r") as file:
                    for line in file:
                        world = json.loads(line)
                        data.append(world)
                for i in data:
                    if i["name"] == world_name:
                        i["languages"][langname] = [langdesc, langback]
                with open(user_worlds, 'w') as file:
                    for obj in data:
                        file.write(json.dumps(obj) + "\n")
                return redirect(url_for("world", world_name=world_name))
            else:
                flash('make sure all fields are filled', 'danger')
                return redirect(url_for("world", world_name=world_name))
            
        if editlangname or editlangdesc or editlangback:
            if editlangname and editlangdesc and editlangback:
                data = []
                with open(user_worlds, "r") as file:
                    for line in file:
                        world = json.loads(line)
                        data.append(world)
                for i in data:
                    if i["name"] == world_name:
                        for lang in i['languages']:
                            if lang == Langforms.HiddenLangName.data:
                                i['languages'][lang] = [editlangdesc, editlangback]
                with open(user_worlds, 'w') as file:
                    for obj in data:
                        file.write(json.dumps(obj) + "\n")
                return redirect(url_for("world", world_name=world_name))
            else:
                flash('make sure all fields are filled', 'danger')
                return redirect(url_for("world", world_name=world_name))
    
        if currplat or currgold or currsilv or currcopp:
            if currplat and currgold and currsilv and currcopp:
                data = []
                with open(user_worlds, "r") as file:
                    for line in file:
                        world = json.loads(line)
                        data.append(world)
                for i in data:
                    if i["name"] == world_name:
                        i["currency"][currplat] = [currgold, currsilv, currcopp]
                with open(user_worlds, 'w') as file:
                    for obj in data:
                        file.write(json.dumps(obj) + "\n")
                return redirect(url_for("world", world_name=world_name))
            else:
                flash('make sure all fields are filled', 'danger')
                return redirect(url_for("world", world_name=world_name))
            
        if editcurrplat or editcurrgold or editcurrsilv or editcurrcopp or editcurrconv:
            if editcurrplat and editcurrgold and editcurrsilv and editcurrcopp and editcurrconv:
                data = []
                with open(user_worlds, "r") as file:
                    for line in file:
                        world = json.loads(line)
                        data.append(world)
                for i in data:
                    if i["name"] == world_name:
                        for curr in i['currency']:
                            if curr == Currforms.HiddenCurrName.data:
                                i['currency'][curr] = [editcurrgold, editcurrsilv, editcurrcopp, editcurrconv]
                with open(user_worlds, 'w') as file:
                    for obj in data:
                        file.write(json.dumps(obj) + "\n")
                return redirect(url_for("world", world_name=world_name))
            else:
                flash('make sure all fields are filled', 'danger')
                return redirect(url_for("world", world_name=world_name))

        if spellname or spelldesc or spellcost or spelldmg:
            if spellname and spelldesc and spellcost and spelldmg:
                data = []
                with open(user_worlds, "r") as file:
                    for line in file:
                        world = json.loads(line)
                        data.append(world)
                for i in data:
                    if i["name"] == world_name:
                        i["magic"][spellname] = [spelldesc, spellcost, spelldmg]
                with open(user_worlds, 'w') as file:
                    for obj in data:
                        file.write(json.dumps(obj) + "\n")
                return redirect(url_for("world", world_name=world_name))
            else:
                flash('make sure all fields are filled', 'danger')
                return redirect(url_for("world", world_name=world_name))
            
        if editspellname or editspelldesc or editspellcost or editspelldmg:
            if editspellname and editspelldesc and editspellcost and editspelldmg:
                data = []
                with open(user_worlds, "r") as file:
                    for line in file:
                        world = json.loads(line)
                        data.append(world)
                for i in data:
                    if i["name"] == world_name:
                        for spell in i['magic']:
                            if spell == Magforms.HiddenSpellName.data:
                                i['magic'][spell] = [editspelldesc, editspellcost, editspelldmg]
                with open(user_worlds, 'w') as file:
                    for obj in data:
                        file.write(json.dumps(obj) + "\n")
                return redirect(url_for("world", world_name=world_name))
            else:
                flash('make sure all fields are filled', 'danger')
                return redirect(url_for("world", world_name=world_name))
            
        if questname or questtask or queststart or questfinish or questreward:
            if questname and questtask and queststart and questfinish and questreward:
                data = []
                with open(user_worlds, "r") as file:
                    for line in file:
                        world = json.loads(line)
                        data.append(world)
                for i in data:
                    if i["name"] == world_name:
                        i["quests"][questname] = [questtask, queststart, questfinish, questreward]
                with open(user_worlds, 'w') as file:
                    for obj in data:
                        file.write(json.dumps(obj) + "\n")
                return redirect(url_for("world", world_name=world_name))
            else:
                flash('make sure all fields are filled', 'danger')
                return redirect(url_for("world", world_name=world_name))
            
        if editquestname or editquesttask or editqueststart or editquestfinish or editquestreward:
            if editquestname and editquesttask and editqueststart and editquestfinish and editquestreward:
                data = []
                with open(user_worlds, "r") as file:
                    for line in file:
                        world = json.loads(line)
                        data.append(world)
                for i in data:
                    if i["name"] == world_name:
                        for quest in i['quests']:
                            if quest == Questforms.HiddenQuestName.data:
                                i['quests'][quest] = [editquesttask, editqueststart, editquestfinish, editquestreward]
                with open(user_worlds, 'w') as file:
                    for obj in data:
                        file.write(json.dumps(obj) + "\n")
                return redirect(url_for("world", world_name=world_name))
            else:
                flash('make sure all fields are filled', 'danger')
                return redirect(url_for("world", world_name=world_name))
            
        if Mapform.Map.data:
            filetypes = session.get('filetypes')
            current = []
            for type in filetypes:
                if os.path.exists(os.path.join(app.config['MAPS_FOLDER'], f"{current_user}_{world_name}_map.{type}")):
                    current.append(f"{current_user}_{world_name}_map.{type}")
            for file in current:
                os.remove(os.path.join(app.config['MAPS_FOLDER'], file))
            # get file from form
            file = Mapform.Map.data
            # make sure the filename is ascii
            filename = secure_filename(file.filename)
            # get the filetype extension
            ext = file.filename.rsplit('.', 1)[1].lower()
            # rename the file
            filename = f"{current_user}_{world_name}_map.{ext}"    
            # append the folder path to the file to make the full file path
            filepath = os.path.join(app.config['MAPS_FOLDER'], filename)
            # save file
            file.save(filepath)
            return redirect(url_for("world", world_name=world_name))       

        # 
        # if none of the other if statements are met
        # 
        else:
            flash("please fill a field", "danger")

    # maybe i should add all the jinja variables to a list or smth so that it doesnt go all the way out there -->                                                                                                                                                                                                                                 
    return render_template(f'world.html', world_name=world_name, current_user=current_user, modules=modules, form=form, Charforms=Charforms, Locforms=Locforms, Histforms=Histforms, Facforms=Facforms, Lawforms=Lawforms, Culforms=Culforms, Techforms=Techforms, Langforms=Langforms, Currforms=Currforms, Magforms=Magforms, Questforms=Questforms, Mapform=Mapform, charfields=charfields, chareditfields=chareditfields, characters=characters, locfields=locfields, loceditfields=loceditfields, locations=locations, histfields=histfields, histeditfields=histeditfields, events=events, facfields=facfields, faceditfields=faceditfields, factions=factions, lawfields=lawfields, laweditfields=laweditfields, laws=laws, culfields=culfields, culeditfields=culeditfields, cultures=cultures, techfields=techfields, techeditfields=techeditfields, technology=technology, langfields=langfields, langeditfields=langeditfields, languages=languages, currfields=currfields, curreditfields=curreditfields, currencies=currencies, magfields=magfields, mageditfields=mageditfields, spells=spells, questfields=questfields, questeditfields=questeditfields, quests=quests, ext=ext)

@app.route('/delete_world/<world_name>', methods=['POST'])
def delete_world(world_name):
    '''
    copilot helped
    how to delete a dictionary from ndjson

    deletes the world from the user's ndjson file.
    '''

    ext = session.get('ext')
    current_user = session.get('current_user')
    file = ""
    if ext:
        file = os.path.join(app.config['MAPS_FOLDER'], f"{current_user}_{world_name}_map.{ext}")
    if file:
        os.remove(file)

    world_name = world_name
    data = []
    user_worlds = session.get('user_worlds')
    # set the condition for deleting a world:
    condition = lambda obj: obj["name"] == world_name
    with open(user_worlds, "r") as file:
        # save all the lines that dont meet the condition:
        for line in file:
            obj = json.loads(line)
            if not condition(obj):
                data.append(obj)
    with open(user_worlds, 'w') as file:
        # write all the saved lines back:
        for obj in data:
            file.write(json.dumps(obj) + "\n")
    # thus all the lines that meet the condition are not written back into the json, and are therefore deleted.

    return redirect(url_for('home'))

@app.route('/delete_char/<char_name>', methods=['GET','POST'])
def delete_char(char_name):
    user_worlds = session.get('user_worlds')
    world_name = session.get('world_name')
    data = []
    kept_chars = {}
    with open(user_worlds, "r") as file:
        for line in file:
            world = json.loads(line)
            data.append(world)
    for world in data:
        if world['name'] == world_name:
            for character in world['characters']:
                if character != char_name:
                    kept_chars[character] = world['characters'][character]
            world['characters'] = kept_chars
    if data:
        with open(user_worlds, 'w') as file:
            for obj in data:
                file.write(json.dumps(obj) + "\n")
    return redirect(url_for("world", world_name=world_name))

@app.route('/delete_loc/<loc_name>', methods=['GET', 'POST'])
def delete_loc(loc_name):
    user_worlds = session.get('user_worlds')
    world_name = session.get('world_name')
    data = []
    kept_locs = {}
    with open(user_worlds, "r") as file:
        for line in file:
            world = json.loads(line)
            data.append(world)
    for world in data:
        if world['name'] == world_name:
            for location in world['locations']:
                if location != loc_name:
                    kept_locs[location] = world['locations'][location]
            world['locations'] = kept_locs
    if data:
        with open(user_worlds, 'w') as file:
            for obj in data:
                file.write(json.dumps(obj) + "\n")
    return redirect(url_for("world", world_name=world_name))

@app.route('/delete_event/<event_name>', methods=['GET', 'POST'])
def delete_event(event_name):
    user_worlds = session.get('user_worlds')
    world_name = session.get('world_name')
    data = []
    kept_events = {}
    with open(user_worlds, "r") as file:
        for line in file:
            world = json.loads(line)
            data.append(world)
    for world in data:
        if world['name'] == world_name:
            for event in world['history']:
                if event != event_name:
                    kept_events[event] = world['history'][event]
            world['history'] = kept_events
    if data:
        with open(user_worlds, 'w') as file:
            for obj in data:
                file.write(json.dumps(obj) + "\n")
    return redirect(url_for("world", world_name=world_name))

@app.route('/delete_fac/<fac_name>', methods=['GET', 'POST'])
def delete_fac(fac_name):
    user_worlds = session.get('user_worlds')
    world_name = session.get('world_name')
    data = []
    kept_facs = {}
    with open(user_worlds, "r") as file:
        for line in file:
            world = json.loads(line)
            data.append(world)
    for world in data:
        if world['name'] == world_name:
            for faction in world['factions']:
                if faction != fac_name:
                    kept_facs[faction] = world['factions'][faction]
            world['factions'] = kept_facs
    if data:
        with open(user_worlds, 'w') as file:
            for obj in data:
                file.write(json.dumps(obj) + "\n")
    return redirect(url_for("world", world_name=world_name))

@app.route('/delete_law/<law_name>', methods=['GET', 'POST'])
def delete_law(law_name):
    user_worlds = session.get('user_worlds')
    world_name = session.get('world_name')
    data = []
    kept_laws = {}
    with open(user_worlds, "r") as file:
        for line in file:
            world = json.loads(line)
            data.append(world)
    for world in data:
        if world['name'] == world_name:
            for law in world['laws']:
                if law != law_name:
                    kept_laws[law] = world['laws'][law]
            world['laws'] = kept_laws
    if data:
        with open(user_worlds, 'w') as file:
            for obj in data:
                file.write(json.dumps(obj) + "\n")
    return redirect(url_for("world", world_name=world_name))

@app.route('/delete_cul/<cul_name>', methods=['GET', 'POST'])
def delete_cul(cul_name):
    user_worlds = session.get('user_worlds')
    world_name = session.get('world_name')
    data = []
    kept_culs = {}
    with open(user_worlds, "r") as file:
        for line in file:
            world = json.loads(line)
            data.append(world)
    for world in data:
        if world['name'] == world_name:
            for cul in world['cultures']:
                if cul != cul_name:
                    kept_culs[cul] = world['cultures'][cul]
            world['cultures'] = kept_culs
    if data:
        with open(user_worlds, 'w') as file:
            for obj in data:
                file.write(json.dumps(obj) + "\n")
    return redirect(url_for("world", world_name=world_name))

@app.route('/delete_tech/<tech_name>', methods=['GET', 'POST'])
def delete_tech(tech_name):
    user_worlds = session.get('user_worlds')
    world_name = session.get('world_name')
    data = []
    with open(user_worlds, "r") as file:
        for line in file:
            world = json.loads(line)
            data.append(world)
    for world in data:
        if world['name'] == world_name:
            world['technology'][tech_name] = ["",""]
            world['technology'][""] = world['technology'].pop(tech_name)
    if data:
        with open(user_worlds, 'w') as file:
            for obj in data:
                file.write(json.dumps(obj) + "\n")
    return redirect(url_for("world", world_name=world_name))

@app.route('/delete_lang/<lang_name>', methods=['GET', 'POST'])
def delete_lang(lang_name):
    user_worlds = session.get('user_worlds')
    world_name = session.get('world_name')
    data = []
    kept_langs = {}
    with open(user_worlds, "r") as file:
        for line in file:
            world = json.loads(line)
            data.append(world)
    for world in data:
        if world['name'] == world_name:
            for lang in world['languages']:
                if lang != lang_name:
                    kept_langs[lang] = world['languages'][lang]
            world['languages'] = kept_langs
    if data:
        with open(user_worlds, 'w') as file:
            for obj in data:
                file.write(json.dumps(obj) + "\n")
    return redirect(url_for("world", world_name=world_name))

@app.route('/delete_curr/<curr_name>', methods=['GET', 'POST'])
def delete_curr(curr_name):
    user_worlds = session.get('user_worlds')
    world_name = session.get('world_name')
    data = []
    kept_currs = {}
    with open(user_worlds, "r") as file:
        for line in file:
            world = json.loads(line)
            data.append(world)
    for world in data:
        if world['name'] == world_name:
            for curr in world['currency']:
                if curr != curr_name:
                    kept_currs[curr] = world['currency'][curr]
            world['currency'] = kept_currs
    if data:
        with open(user_worlds, 'w') as file:
            for obj in data:
                file.write(json.dumps(obj) + "\n")
    return redirect(url_for("world", world_name=world_name))

@app.route('/delete_spell/<spell_name>', methods=['GET', 'POST'])
def delete_spell(spell_name):
    user_worlds = session.get('user_worlds')
    world_name = session.get('world_name')
    data = []
    kept_spells = {}
    with open(user_worlds, "r") as file:
        for line in file:
            world = json.loads(line)
            data.append(world)
    for world in data:
        if world['name'] == world_name:
            for spell in world['magic']:
                if spell != spell_name:
                    kept_spells[spell] = world['magic'][spell]
            world['magic'] = kept_spells
    if data:
        with open(user_worlds, 'w') as file:
            for obj in data:
                file.write(json.dumps(obj) + "\n")
    return redirect(url_for("world", world_name=world_name))

@app.route('/delete_quest/<quest_name>', methods=['GET', 'POST'])
def delete_quest(quest_name):
    user_worlds = session.get('user_worlds')
    world_name = session.get('world_name')
    data = []
    kept_quests = {}
    with open(user_worlds, "r") as file:
        for line in file:
            world = json.loads(line)
            data.append(world)
    for world in data:
        if world['name'] == world_name:
            for quest in world['quests']:
                if quest != quest_name:
                    kept_quests[quest] = world['quests'][quest]
            world['quests'] = kept_quests
    if data:
        with open(user_worlds, 'w') as file:
            for obj in data:
                file.write(json.dumps(obj) + "\n")
    return redirect(url_for("world", world_name=world_name))

@app.route('/delete_map/<world_name>', methods=['GET','POST'])
def delete_map(world_name):
    ext = session.get('ext')
    current_user = session.get('current_user')
    file = os.path.join(app.config['MAPS_FOLDER'], f"{current_user}_{world_name}_map.{ext}")
    os.remove(file)
    return redirect(url_for("world", world_name=world_name))

@app.route('/delete_account', methods=['GET','POST'])
def delete_account():
    current_user = session.get('current_user')
    cursor = DB.cursor()
    cursor.execute("DELETE FROM Users WHERE username=?", [current_user])
    DB.commit()
    user_worlds = session.get('user_worlds')
    filetypes = session.get('filetypes')
    data = []
    if os.path.exists(user_worlds):
        with open(user_worlds, "r") as file:
                    for line in file:
                        world = json.loads(line)
                        data.append(world)     
        for world in data:
            world_name = world['name']
            for ext in filetypes:
                file = os.path.join(app.config['MAPS_FOLDER'], f"{current_user}_{world_name}_map.{ext}")
                if os.path.exists(file):
                    os.remove(file)
        os.remove(user_worlds)
    session['current_user'] = None
    flash('Account successfully deleted', 'success')
    return redirect(url_for("welcome"))

@app.route('/logout', methods=['GET','POST'])
def logout():
    session['current_user'] = None
    return redirect(url_for('welcome'))

if __name__ == '__main__': # runs if file is run as script, but not if its imported
    app.run(debug=True, port=5000, host="0.0.0.0")