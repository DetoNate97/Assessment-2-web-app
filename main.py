from flask import Flask, render_template, url_for, redirect, flash
from forms import RegisterForm, LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'b18b7463547b20e1da73aeb67a7658d2' # change
current_user = ""

@app.route('/')
def welcome():
    '''
    Handles rendering of the landing page of the website. its the page the viewer first sees
    renders the welcome.html and returns it to be viewed.

    Parameters:
        None

    Returns:
        A rendered html
    '''
    return render_template('welcome.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    '''
    Handles rendering of the login page.
    renders the login.html, sends the form to the html, validates the submitted form, and logs in the user, saves the username to current_user.

    Parameters:
        none

    Returns:
        A rendered html
        or
        A redirect to the home page after a successful login
    '''
    global current_user
    page = "Log In"
    form = LoginForm()
    log_user, log_pass, fields = form.FloatingUsername.data, form.FloatingPassword.data, form.fields
    current_user = log_user
    if form.validate_on_submit():
        print(log_user, log_pass)
        flash('','success')
        return redirect(url_for('home'))
    else:
        flash('','danger')
    return render_template('login.html', page=page, form=form, fields=fields)

@app.route('/register', methods=['GET', 'POST'])
def register():
    '''
    Handles rendering of the register page.
    renders the register.html, sends the form to the html, validates the submitted form, adds the new user to the database, and logs in the user.

    Parameters:
        none

    Returns:
        A rendered html
        or
        A redirect to the home page after a successful login
    '''
    global current_user
    page="Register"
    form = RegisterForm()
    reg_user, reg_email, reg_pass = form.FloatingUsername.data, form.FloatingEmail.data, form.FloatingPassword.data
    current_user = reg_user
    if form.validate_on_submit():
        print(reg_user, reg_pass, reg_email)
        flash('','success')
        return redirect(url_for('home'))
    else:
        flash('','danger')
    return render_template('register.html', page=page, form=form, fields=form.fields)

@app.route('/home')
def home():
    '''
    Handles rendering of the home page.
    (slightly inspired by google docs)

    This route (idk)<-later
    renders the home.html and then returns it to be viewed.

    Parameters:
        none

    Returns:
        A rendered html
    '''
    global current_user
    page = "home"
    return render_template('home.html', page=page, user=current_user)

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
    app.run(debug=True, port=5000)