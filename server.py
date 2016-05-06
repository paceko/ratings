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
    user = User.query.filter_by(email=email).first()


    if user:
        #check if password matched
        if user.password == password:
            #create the key value pair in the session(= magic dictionary)
            #(flask's session)
            session['user_id'] = user.user_id
        #yes, flash you are log in
            flash("You have been logged in.")
            location = "/users/"+ str(user.user_id)
            return redirect(location)
        else:
            flash("Your password was incorrect.")
            return redirect('/login_page')
        #no, the password didnt match try again
        #re-route them to the sign-in page
    else:
        # add new user to db
        user = User(email=email, password=password)
        db.session.add(user)
        db.session.commit()
        #log them in
        flash("yeah you are now signed up. please login.")
        return redirect('/login_page')

@app.route("/logout")
def logout():
    """Logs out user and flashes a logout message"""

    # deletes the key and value in the session dictionary
    del session['user_id']
    flash("You have been logged out.")
    return redirect('/') 

@app.route("/users/<int:user_id>")
def display_user_details(user_id):
    """display user details in the movies they have rated"""

    user = User.query.filter_by(user_id=user_id).one()
    
    #list of ratings objects that we got from the 
    #user and ratings relationship in model.py 
    ratings = user.ratings

    #passing the user object & list of ratings objects to the template
    return render_template ("user_info.html", user=user, ratings=ratings)

# getting /movies from the link on the homepage.html
@app.route("/movies")
def display_movies():
    """Displays list of movie titles"""

#order by movie title
    movies = Movie.query.order_by('title').all()

    return render_template ("movie_list.html", movies=movies)

@app.route("/movie/<int:movie_id>")
def display_movie_details(movie_id):
    """Displays the details about the movie"""

    movie = Movie.query.filter_by(movie_id=movie_id).one()

    return render_template ("movie_details.html", movie=movie)

@app.route("/rate_movie/<int:movie_id>", methods=["POST"])
def rating_movie(movie_id):
    """Set a rating for a movie"""

    user_id = session.get('user_id')
    #if user id is none make them sign in
    if not user_id:
        #redirect to login page so that user can sign in
        flash("You have to sign in!")
        return redirect("/login_page")

    new_score = request.form.get('rating')
    #check to see if user_id has rated movie_id
    rating = Rating.query.filter_by(movie_id=movie_id, user_id=user_id).first()
    #if yes, then update rating score
    if rating:
    #take object rating select it attribute score and reassign a new score to it
        rating.score = new_score
    #adding object to SQL Alchemy session
        db.session.add(rating)
    #saving it to the database
        db.session.commit()
        flash("You updated your rating!")
        return redirect("/movie/" + str(movie_id)) 

    else:    
    #if no, create a new rating
        new_rating = Rating(movie_id=movie_id, user_id=user_id, score=new_score)
        #add to db
        db.session.add(new_rating)
        #save to the database
        db.session.commit()
        flash("You rated that movie!")
        return redirect("/movie/" + str(movie_id))

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()
