from flask import Flask, render_template, url_for, redirect, flash, session
from forms import RegisterForm, LoginForm, CustomSelectForm
import os, sqlite3, secrets, json
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
key = Fernet.generate_key() # i should prob make this a const...
cipher = Fernet(key)
key = key.decode()
salt = os.urandom(16)

def hash_password(password):
    '''
    currently unused function. hashes the input and returns it.
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
    print(f"Connected")
except sqlite3.OperationalError as error:
    print(f"Error: {error}")

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
    global key
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
            cursor.execute("INSERT INTO Users (username, email, password, key) VALUES (?, ?, ?, ?)", (reg_user, reg_email, f"{encrypt_message(reg_pass)}", key))
            cursor.execute(f"CREATE TABLE User_{reg_user}_Worlds (id INTEGER PRIMARY KEY AUTOINCREMENT, WorldName TEXT NOT NULL)") # delete
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
    Handles the home page. this is where all the cards for the user's worlds are displayed. slightly inspired by google docs/canvas.

    Methods: 
    GET: render the home.html with the form in the modal.
    POST: validate the submitted data, create a new world with the selected modules.
    '''
    form = CustomSelectForm()
    CharFields, SettFields, GameFields = form.CharacterFields, form.SettingFields, form.GameplayFields # split bc there are subheadings
    fields=form.fields # why is this here
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
    else:
        if form.validate_on_submit():
            # delete:
            cursor = DB.cursor()
            cursor.execute(f"INSERT INTO User_{current_user}_Worlds (WorldName) VALUES (?)", ("test",))
            DB.commit()
            # record the selected modules:
            modules = []
            for i in form.CharacterFields:
                if form[i].data:
                    modules.append(i)
            for i in form.SettingFields:
                if form[i].data:
                    modules.append(i)
            for i in form.GameplayFields:
                if form[i].data:
                    modules.append(i)
            # (temp):
            print("saved modules: ", modules)
            session['world_modules'] = modules
            # create the world in the json file:
            data = {
                "name": "custom", 
                "modules": modules
                }
            with open(user_worlds, "a") as file:
                file.write(json.dumps(data) + "\n")
            return redirect(url_for('world', world_name="custom"))
        return render_template('home.html', page=page, user=current_user, form=form, fields=fields, CharFields=CharFields, SettingFields=SettFields, GameFields=GameFields, data=data)    

@app.route('/settings')
def settings():
    '''
    Handles rendering of the settings page. slightly inspired by microsoft edge settings

    methods
    '''
    page = "settings"
    return render_template('settings.html', page=page)

@app.route('/run_function', methods=['POST'])
def run_function():
    '''
    test function
    '''
    print("Button was clicked!")
    return redirect(url_for('home'))

@app.route('/run_function_book', methods=['POST'])
def run_function_book():
    '''
    enters "book" into the db for the user's worlds and redirects to the world page.
    '''
    modules = ['CharCreator', 'Historical', 'Maps', 'Locations', 'Hierarchy', 'Factions', 'Laws', 'Cultures', 'Technology', 'Languages', 'Currency'] # set the preset modules
    # create the new world in the json file:
    user_worlds = session.get('user_worlds')
    data = {
        "name": "book", 
        "modules": modules
        }
    with open(user_worlds, "a") as file:
        file.write(json.dumps(data) + "\n")
    # delete:
    current_user = session.get('current_user')
    cursor = DB.cursor()
    cursor.execute(f"INSERT INTO User_{current_user}_Worlds (WorldName) VALUES (?)", ("book",))
    DB.commit()
    # store the selected modules (temp):
    session['world_modules'] = modules

    return redirect(url_for('world', world_name="book"))

@app.route('/run_function_movie', methods=['POST'])
def run_function_movie():
    '''
    enters "movie" into the db for the user's worlds
    '''
    current_user = session.get('current_user')
    cursor = DB.cursor()
    cursor.execute(f"INSERT INTO User_{current_user}_Worlds (WorldName) VALUES (?)", ("movie",))
    DB.commit()
    return redirect(url_for('home', world_name=""))

@app.route('/run_function_game', methods=['POST'])
def run_function_game():
    '''
    enters "game" into the db for the user's worlds
    '''
    current_user = session.get('current_user')
    cursor = DB.cursor()
    cursor.execute(f"INSERT INTO User_{current_user}_Worlds (WorldName) VALUES (?)", ("game",))
    DB.commit()
    return redirect(url_for('home'))

world_name = "example_world"
@app.route(f'/world/<world_name>')
def world(world_name):
    '''
    Handles the custom worlds.
    instead of somehow creating an individual html file for each world, this instead is a single file that gets all the data for the world and displays it.

    param:
    world name: ............................ activate dem neurons
    '''
    modules = session.get('world_modules')
    current_user = session.get('current_user')
    if not current_user:
        return redirect(url_for("login"))

    return render_template(f'world.html', world_name=world_name, modules=modules)

if __name__ == '__main__': # runs if file is run as script, but not if its imported
    app.run(debug=True, port=5000, host="0.0.0.0")
    # make a start.bat file