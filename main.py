from flask import Flask, render_template, url_for, redirect, flash
from forms import RegisterForm, LoginForm, CustomSelectForm
import os, sqlite3, secrets
from cryptography.fernet import Fernet
# alternate encryption modules:
# import hashlib, zlib
# print(hashlib.algorithms_available)
# password = input("Enter a password: ")
# hashed_password = hashlib.sha256(password.encode()).hexdigest()
# print("Hashed password:", hashed_password)

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
current_user = ""
key = Fernet.generate_key()
cipher = Fernet(key)
key = key.decode()
# print(key)
# key = b'-SB8UllACGvAHyRGhJGxgiwl5-UuxUfNAcY3BRvZMSI='
# cipher = Fernet(key)

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

# database file path
db_path = os.path.join("database", "database.db")
'''change path to fit venv location'''

# connect to the database. 
try:
    db = sqlite3.connect(db_path, check_same_thread=False) # "check_same_thread=False" fix used from assessment 1.
    print(f"Connected")
except sqlite3.OperationalError as error:
    print(f"Error: {error}")

@app.route('/')
def welcome():
    '''
    Handles rendering of the landing page of the website. its the page the viewer first sees.
    Returns a rendered html.
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
    global current_user, db
    page, form = "Log In", LoginForm()
    fields = form.fields
    if form.validate_on_submit():
        log_user, log_pass = str(form.FloatingUsername.data), str(form.FloatingPassword.data)
        db_data = db.execute("SELECT password,key FROM Users WHERE username = ?", [log_user]).fetchall() # db_data is in the format [("password", "key")]. why, sql, why.
        if not db_data:
            flash(f'Failed to log in, user {log_user} does not exist', 'danger')
        else: 
            db_password = db_data[0][0]
            db_key = db_data[0][1]
            db_password = decrypt_message(db_password, db_key)  
            if db_password == log_pass:
                flash(f'Successfully logged in user {log_user}!', 'success')
                current_user = log_user
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
    global current_user, db, key
    page, form = "Register", RegisterForm()
    fields = form.fields
    if form.validate_on_submit():
        reg_user, reg_email, reg_pass = str(form.FloatingUsername.data), str(form.FloatingEmail.data), str(form.Password.data)
        if not db.execute( f"SELECT password FROM Users WHERE username = ?", [reg_user] ).fetchall():
            cursor = db.cursor()
            cursor.execute("INSERT INTO Users (username, email, password, key) VALUES (?, ?, ?, ?)", (reg_user, reg_email, f"{encrypt_message(reg_pass)}", key)) # save new user to db
            # create user's worlds db: cursor.execute(f"CREATE TABLE User_{reg_user}_Worlds (id INTEGER PRIMARY KEY AUTOINCREMENT, account_holder TEXT NOT NULL, account_name TEXT NOT NULL, balance INTEGER)")
            db.commit()
            current_user = reg_user
            flash(f'Account created for {form.FloatingUsername.data}!', 'success')
            return redirect(url_for('home'))
        else:
            flash(f'Failed to create account: account name already exists.', 'danger')
    return render_template('register.html', page=page, form=form, fields=fields)

@app.route('/home', methods=['GET', 'POST'])
def home():
    '''
    Handles rendering of the home page. this is where all the cards for the user's worlds are displayed. slightly inspired by google docs. 
    renders the home.html, checks if current_user doesnt exist and redirects to login

    Returns:
        A rendered html
        or
        A redirect to login if there is no current_user
    '''
    form = CustomSelectForm()
    CharFields = form.CharacterFields
    SettingFields = form.SettingFields
    GameFields = form.GameplayFields
    fields=form.fields

    global current_user
    page = "home"
    if not current_user:
        return redirect(url_for("login"))
    else:
        if form.validate_on_submit():
            pass
        return render_template('home.html', page=page, user=current_user, form=form, fields=fields, CharFields=CharFields, SettingFields=SettingFields, GameFields=GameFields)    

@app.route('/settings')
def settings():
    '''
    Handles rendering of the settings page.
    (slightly inspired by microsoft edge settings)

    This route (edits x setting, etc)<-later
    renders the settings.html and then returns it to be viewed.

    Parameters:
        none

    Returns:
        A rendered html
    '''
    page = "settings"
    return render_template('settings.html', page=page)

world_name = "example_name"
@app.route(f'/{world_name}')
def world_1(): # figure out how to make procedural
    '''
    Handles rendering of the home page of a user's custom world.

    This route (edits x features of the world, etc)<-later
    renders the world's .html and then returns it to be viewed.

    Parameters:
        none

    Globals:
        world_name : the name of the world to be rendered (temporary)
        
    Returns:
        A rendered html
    '''
    return render_template(f'{world_name}.html')

if __name__ == '__main__': # runs if file is run as script, but not if its imported
    app.run(debug=True, port=5000, host="0.0.0.0")