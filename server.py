"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session

from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Rating, Movie


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")

@app.route("/users")
def user_list():
    """Show list of users"""

    users = User.query.all()
    return render_template("user_list.html", users=users)

@app.route("/login_page")
def sign_in_form():
    """Show login page"""

    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    """Log in user or create new user"""

    #check to see if the user is in db
    email = request.form.get("email")
    password = request.form.get("pwd")

    #if yes log them in. 
    #Checking to see if the email is already in the database
    user = Users.query.filter_by(email=email).all()
    
    if user:
        #check if password matched
        user.password == password
        #yes, flash you are log in
        #no, the password didnt match try again
        #re-route them to the sign-in page
    else:
        # add new user to db
        user = User(email=email, password=password)
        db.session.add(user)
        db.session.commit()
        #log them in


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()
