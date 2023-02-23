from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from forms.edit import Edit
from forms.add import Add
import requests
import os
from dotenv import load_dotenv

load_dotenv()

MOVIE_KEY = os.getenv("movie_key")
MOVIE_DB_INFO_URL = "https://api.themoviedb.org/3/movie"
MOVIE_DB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"
MOVIE_DB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


with app.app_context():
    db = SQLAlchemy(app)


    class Movie(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(50))
        year = db.Column(db.Integer)
        description = db.Column(db.String(50))
        rating = db.Column(db.Float)
        ranking = db.Column(db.Integer)
        review = db.Column(db.String(250))
        img_url = db.Column(db.String(250))

    db.create_all()

    # movie1 = Movie(
    #     title="Phone Booth",
    #     year=2002,
    #     description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
    #     rating=7.3,
    #     ranking=10,
    #     review="My favourite character was the caller.",
    #     img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
    # )
    # db.session.add(movie1)
    # db.session.commit()

@app.route("/")
def home():
    movies = db.session.query(Movie).order_by(Movie.rating.desc()).all()
    return render_template("index.html",movies=movies)

@app.route("/edit_card/<int:v>",methods=["GET","PATCH","POST"])
def edit_card(v):
    movie = Movie.query.get(v)
    form = Edit()
    if form.validate_on_submit():
        movie.rating = form.data["rating"] 
        movie.review = form.data["review"]
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("edit.html",form=form,movie=movie)

@app.route("/delete_card/<int:v>")
def delete_card(v):
    movie = Movie.query.get(v)
    db.session.delete(movie)
    db.session.commit() 
    return redirect(url_for("home"))

@app.route("/add",methods=["GET","POST"])
def add_card():
    #Add another form and if validates on submits 
    form = Add()
    if form.validate_on_submit():
        title=form.data["title"]          
        params = {
            "api_key":MOVIE_KEY,
            "language":"en-US",
            "query": title,
            "page":1
        }
        response = requests.get("https://api.themoviedb.org/3/search/movie",params=params)
        movies = response.json()["results"]
        # url format is https://image.tmdb.org/t/p/w440_and_h660_face/70PQCYF3ExuKHqyieJhYV0GJg9H.jpg
        return render_template("select.html",movies=movies)
    return render_template("add.html",form=form)

@app.route("/find")
def find_movie():
    movie_api_id = request.args.get("id")
    if movie_api_id:
        movie_api_url = f"{MOVIE_DB_INFO_URL}/{movie_api_id}"
        #The language parameter is optional, if you were making the website for a different audience 
        #e.g. Hindi speakers then you might choose "hi-IN"
        response = requests.get(movie_api_url, params={"api_key": MOVIE_KEY, "language": "en-US"})
        data = response.json()
        new_movie = Movie(
            title=data["title"],
            #The data in release_date includes month and day, we will want to get rid of.
            year=data["release_date"].split("-")[0],
            img_url=f"{MOVIE_DB_IMAGE_URL}{data['poster_path']}",
            description=data["overview"]
        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for("edit_card",v=new_movie.id))
if __name__ == '__main__':
    app.run(debug=True)
