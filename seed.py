"""Utility file to seed ratings database from MovieLens data in seed_data/"""

from sqlalchemy import func
from model import User
import datetime 
from model import Rating
from model import Movie

from model import connect_to_db, db
from server import app


def load_users():
    """Load users from u.user into database."""

    print "Users"

    # Delete all rows in table, so if we need to run this a second time,
    # we won't be trying to add duplicate users
    User.query.delete()

    # Read u.user file and insert data
    for row in open("seed_data/u.user"):
        row = row.rstrip()
        user_id, age, gender, occupation, zipcode = row.split("|")

        user = User(user_id=user_id,
                    age=age,
                    zipcode=zipcode)

        # We need to add to the session or it won't ever be stored
        db.session.add(user)

    # Once we're done, we should commit our work
    db.session.commit()


def load_movies():
    """Load movies from u.item into database."""

    print "Movies"
    # empties the table (against duplicates)
    Movie.query.delete()

    for row in open("seed_data/u.item"):
        row = row.rstrip()
        movie_id, title, released_str, imdb_url = row.split("|")[:4]

        #finding the index of first open parenthesis () in the title
        # num = title.find("(")

        # #rebinding title to a slice of the title- removing all chars after num
        # title = title[:num-1]
        #removes the last 7 char of the title that have the extra year
        title = title[:-7]

        if released_str:
            released_at = datetime.datetime.strptime(released_str, "%d-%b-%Y")
        else:
            released_at = None

        #create the object of the class Movie
        movie = Movie(movie_id=movie_id,
                        title=title,
                        released_at=released_at,
                        imdb_url=imdb_url)
        #create an entry for database 
        db.session.add(movie)
        # saves it to database
    db.session.commit()


def load_ratings():
    """Load ratings from u.data into database."""

    print "Ratings"

    Rating.query.delete()

    for row in open("seed_data/u.data"):
        row = row.rstrip()
        user_id, movie_id, score, timestamp = row.split("\t")

        rating = Rating(user_id=user_id,
                    movie_id=movie_id,
                    score=score)

        db.session.add(rating)

    db.session.commit()

def set_val_user_id():
    """Set value for the next user_id after seeding database"""

    # Get the Max user_id in the database
    result = db.session.query(func.max(User.user_id)).one()
    max_id = int(result[0])

    # Set the value for the next user_id to be max_id + 1
    query = "SELECT setval('users_user_id_seq', :new_id)"
    # SQLAlch. statement that takes two arguments  query and takes 
    # dictionary (Python) as a value. The key for the dictionary has to
    # match the value that is entered in the SQL query

    db.session.execute(query, {'new_id': max_id + 1})
    db.session.commit()

def set_val_movie_id():
    """Set value for the next user_id after seeding database"""

    result = db.session.query(func.max(Movie.movie_id)).one()
    max_id = int(result[0])

    query = "SELECT setval('movies_movie_id_seq', :new_id)"
    db.session.execute(query, {'new_id': max_id +1})
    db.session.commit()



if __name__ == "__main__":
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    # Import different types of data
    load_users()
    load_movies()
    load_ratings()
    set_val_user_id()
