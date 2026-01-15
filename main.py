from flask import Flask, render_template #, redirect, url_for

app = Flask(__name__)

@app.route('/')
def landing():
    '''
    Handles rendering of the landing page of the website.

    This route renders the landing.html and returns it to be viewed.

    Parameters:
        none

    Returns:
        A rendered html
    '''
    return render_template('landing.html')

@app.route('/login')
def login():
    '''
    Handles rendering of the login page.

    This route (shows a login form, validates the submitted form, logs in the user)<-later
    renders the login.html and then returns it to be viewed.

    Parameters:
        none

    Returns:
        A rendered html
        or
        A redirect to the home page after a successful login
    '''
    return render_template('login.html')

@app.route('/register')
def register():
    '''
    Handles rendering of the register page.

    This route (shows a register form, validates the submitted form, creates a new user, logs in the user)<-later
    renders the register.html and then returns it to be viewed.

    Parameters:
        none

    Returns:
        A rendered html
        or
        A redirect to the home page after a successful login
    '''
    return render_template('register.html')

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
    return render_template('home.html')

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
    return render_template('settings.html')

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