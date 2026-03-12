from flask import Flask, render_template, url_for, redirect, flash, session
from flask_login import login_user, logout_user # not used, but remember to use next time i need to make a login
from forms import RegisterForm, LoginForm, CustomSelectForm, ChangeWorldNameForm, CharForms
import os, sqlite3, secrets, json, time
from cryptography.fernet import Fernet
from werkzeug.security import generate_password_hash, check_password_hash


# alternate security modules: import hashlib, zlib
# print(hashlib.algorithms_available)
# output = hashlib.sha256(input.encode()).hexdigest()

# switched from hashlib to werkzeug because generate_password_hash does exactly the same thing but i dont have to code it.
# also encryption doesnt work when the key changes so the key needs to be stored as well to even read or compare the password for logins.
# but that is basically storing the key and lock in the same place so defeats the purpose of encrypting it in the first place.
# reminder to switch to just hashing it so i dont need to store the key...

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
key = Fernet.generate_key()
cipher = Fernet(key)
KEY = key.decode()
salt = os.urandom(16) # is this even used for anything? no, me, it isnt.

def hash_password(password):
    '''
    currently unused function. hashes the input using werkzeug and returns it.
    here as a reminder to use this method of hashing instead of the current method of encrypting.
    '''
    return generate_password_hash(password)

def encrypt_message(msg):
    '''
    encrypts the input message with the generated encryption key
    
    Parameters:
        msg(str): the string to be encrypted

    Returns:
        an encrypted string
    '''
    return (cipher.encrypt(msg.encode())).decode()
    
def decrypt_message(msg, key):
    '''
    decrypts the input message with the generated encryption key
    
    Parameters:
        msg(str): the string to be decrypted

    Returns:
        a decrypted string
    '''
    cipher = Fernet(key.encode())
    return (cipher.decrypt(msg.encode())).decode()

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
        db_data = DB.execute("SELECT password,key FROM Users WHERE username = ?", [log_user]).fetchall() # db_data is in the format [("password", "key")]. why, sql, why.
        # check if there is a stored password:
        if not db_data: 
            flash(f'Failed to log in, user {log_user} does not exist', 'danger')
        else: 
            db_password = db_data[0][0] # gets the data out of the stupid double tuple trouble.
            db_key = db_data[0][1]
            db_password = decrypt_message(db_password, db_key)  
            # compare input and stored passwords:
            if db_password == log_pass:
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
            cursor.execute("INSERT INTO Users (username, email, password, key) VALUES (?, ?, ?, ?)", (reg_user, reg_email, f"{encrypt_message(reg_pass)}", KEY))
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
        else:
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
        with open(user_worlds, "a") as file:
            file.write(json.dumps(data) + "\n")
        return redirect(url_for('world', world_name=world_name))
    return render_template('home.html', page=page, user=current_user, form=form, fields=fields, worldnamefield=worldnamefield, CharFields=CharFields, SettFields=SettFields, GameFields=GameFields, data=data)    

@app.route('/settings')
def settings():
    '''
    Handles rendering of the settings page. slightly inspired by microsoft edge settings

    methods
    '''
    page = "settings"
    return render_template('settings.html', page=page)

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
        print("no db? :megamind:") # can just delete this
    for i in data:
        if i["name"] == world_name:
            modules = i["modules"]
            pass # for some reason pass works here but the one to change name needs break
    session['world_modules'] = modules
    session['world_name'] = world_name # added for delete char. probably would have been useful for other stuff earlier.
    return redirect(url_for('world', world_name=world_name))

# rename these to create_new_(text). also they broken again
@app.route('/run_function_book', methods=['POST'])
def run_function_book():
    '''
    redirects to the world. similar to the open_world function, but instead of opening the modal to select modules, they are preselected.
    creates the world in the json with pre-set modules and redirects to it.

    returns:
    a redirect to the world
    '''
    modules = ['CharCreator', 'Historical', 'Maps', 'Locations', 'Hierarchy', 'Factions', 'Laws', 'Cultures', 'Technology', 'Languages', 'Currency'] # set the preset modules
    # create the new world in the json file:
    user_worlds = session.get('user_worlds')
    data = {
        "name": "New_Book", 
        "modules": modules
        }
    with open(user_worlds, "a") as file:
        file.write(json.dumps(data) + "\n")
    # store the selected modules:
    session['world_modules'] = modules
    return redirect(url_for('world', world_name="New_Book"))

@app.route('/run_function_movie', methods=['POST'])
def run_function_movie():
    '''
    redirects to the world. the movie preset alternative to run_function_book.
    creates the world in the json with pre-set modules and redirects to it.

    returns:
    a redirect to the world
    '''
    modules = ['CharCreator', 'Historical', 'Maps', 'Locations', 'Hierarchy', 'Factions', 'Laws', 'Cultures', 'Technology', 'Languages', 'Currency'] # set the preset modules
    # create the new world in the json file:
    user_worlds = session.get('user_worlds')
    data = {
        "name": "New_Movie", 
        "modules": modules
        }
    with open(user_worlds, "a") as file:
        file.write(json.dumps(data) + "\n")
    # store the selected modules:
    session['world_modules'] = modules
    return redirect(url_for('world', world_name="New_Movie"))

@app.route('/run_function_game', methods=['POST'])
def run_function_game():
    '''
    redirects to the world. the videogame preset alternative to run_function_book.
    creates the world in the json with pre-set modules and redirects to it.

    returns:
    a redirect to the world
    '''
    modules = ["CharCreator", "Historical", "Maps", "Locations", "Hierarchy", "Factions", "Laws", "Cultures", "Technology", "Languages", "Currency", "Gameplay", "Magic", "Quests"] # set the preset modules
    # create the new world in the json file:
    user_worlds = session.get('user_worlds')
    data = {
        "name": "New_Game", 
        "modules": modules
        }
    with open(user_worlds, "a") as file:
        file.write(json.dumps(data) + "\n")
    # store the selected modules:
    session['world_modules'] = modules
    return redirect(url_for('world', world_name="New_Game"))

@app.route(f'/world/<world_name>', methods=['GET', 'POST'])
def world(world_name):
    '''
    Handles the custom worlds.
    instead of somehow creating an individual html file for each world, this instead is a single file that gets all the data for the world and displays it.

    parameters:
    world name: ............................ activate dem neurons

    returns:
    a rendered html
    '''
    modules = session.get('world_modules')
    current_user = session.get('current_user')
    user_worlds = session.get('user_worlds')
    data = []
    form = ChangeWorldNameForm()
    Charforms = CharForms()
    charfields = Charforms.CharFields
    editfields = Charforms.EditFields

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
    # if the form is submitted, check which fields have been filled
    if form.validate_on_submit():
        # this section is really long so i added big gaps
        # since there are many forms on this one page, it needs to check which one was filled and submitted

        #
        # set all the fields to a variable for easy checking
        #
        charname = Charforms.CreateCharacterNameField.data
        charinfo = Charforms.CreateCharacterInfoField.data
        extrainfo = Charforms.extrafield.data
        editcharname = Charforms.ChangeCharacterName.data
        editcharinfo = Charforms.ChangeCharacterInfo.data
        editextrainfo = Charforms.changeextrafield.data

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
            if not charname and not charinfo and not extrainfo:
                return redirect(url_for("world", world_name=form.worldnamefield.data))
        
        #
        # check if any of the character creation fields were filled
        #
        if charname or charinfo or extrainfo:
            if charname and charinfo and extrainfo:
                with open(user_worlds, "r") as file:
                    for line in file:
                        world = json.loads(line)
                        data.append(world)
                for i in data:
                    if i["name"] == world_name:
                        i["characters"][charname] = [charinfo, extrainfo]
                with open(user_worlds, 'w') as file:
                    for obj in data:
                        file.write(json.dumps(obj) + "\n")
                return redirect(url_for("world", world_name=world_name))
            else:
                flash('please fill all fields', 'danger')

        #
        # check if any of the edit fields were filled
        #
        if editcharname or editcharinfo or editextrainfo:
            if editcharname and editcharinfo and editextrainfo:
                with open(user_worlds, "r") as file:
                    for line in file:
                        world = json.loads(line)
                        data.append(world)
                for i in data:
                    if i["name"] == world_name:
                        for char in i['characters']:
                            if char == Charforms.hiddencharname.data:
                                i['characters'][char] = [editcharinfo, editextrainfo]
                with open(user_worlds, 'w') as file:
                    for obj in data:
                        file.write(json.dumps(obj) + "\n")
                return redirect(url_for("world", world_name=world_name))
            else:
                flash('make sure all fields are filled', 'danger')
                return redirect(url_for("world", world_name=world_name))       

        # 
        # if none of the other if statements are met
        # 
        else:
            flash("please fill a field", "danger")
        # why do these if statements act like elif statements?
        # FIGURED IT OUT: EACH SUBMIT ONLY SUBMITS ITS OWN FIELDS, SO ALL THE OTHERS ARE EMPTY EVEN IF THEY HAVE DATA
        # anyway make sure every combination of filled and unfilled fields has an outcome that doesnt crash

    # maybe i should add all the jinja variables to a list or smth so that it doesnt go all the way out there -->                                                                              here
    return render_template(f'world.html', world_name=world_name, modules=modules, form=form, Charforms=Charforms, charfields=charfields, editfields=editfields, characters=characters, editdata="")

@app.route('/delete_world/<world_name>', methods=['POST'])
def delete_world(world_name):
    '''
    copilot helped
    how to delete a dictionary from ndjson
    '''
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
    # damn im bringing english into this now
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

if __name__ == '__main__': # runs if file is run as script, but not if its imported
    app.run(debug=True, port=5000, host="0.0.0.0")