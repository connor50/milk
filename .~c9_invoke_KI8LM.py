from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import gettempdir
import requests
from analyzer import Analyzer
from helpers import *

# configure application
app = Flask(__name__)

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = gettempdir()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure application
app = Flask(__name__)

app.secret_key = 'F12Zr47j\3yX R~X@H!jmM]Lwf/,?KT'

@app.route("/deliver", methods=["GET", "POST"])
def deliver():
    if request.method == "GET" or request.method == "POST":
        return render_template("register.html")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        session["milk"] = request.form['milk']
        news = getnews(session["milk"])
        if session["milk"] == "chocolate":
            return render_template("chocolate.html", milk=request.form['milk'], news=news)
        elif session["milk"] == "skimmed":
            return render_template("skimmed.html", milk=request.form['milk'], news=news)
        elif session["milk"] == "whole":
            return render_template("whole.html", milk=request.form['milk'], news=news)
    else:
        return render_template("index.html")
    # ask for current milk status 
    
def getnews(milk):

    """ aggregate news """
    bbc = requests.get("https://newsapi.org/v1/articles?source=bbc-news&sortBy=top&apiKey=6ef0dce6d16e45ffa1fdd01274f57bc2")
    bbc = bbc.json()
    
    nytimes = requests.get("https://newsapi.org/v1/articles?source=the-new-york-times&sortBy=top&apiKey=6ef0dce6d16e45ffa1fdd01274f57bc2")
    nytimes = nytimes.json()
    
    google = requests.get("https://newsapi.org/v1/articles?source=google-news&sortBy=top&apiKey=6ef0dce6d16e45ffa1fdd01274f57bc2")
    google = google.json()
    
    independent = requests.get("https://newsapi.org/v1/articles?source=independent&sortBy=top&apiKey=6ef0dce6d16e45ffa1fdd01274f57bc2")
    independent = independent.json()
    
    economist = requests.get("https://newsapi.org/v1/articles?source=the-economist&sortBy=top&apiKey=6ef0dce6d16e45ffa1fdd01274f57bc2")
    economist = economist.json()
    
    guardian = requests.get("https://newsapi.org/v1/articles?source=the-guardian-uk&sortBy=top&apiKey=6ef0dce6d16e45ffa1fdd01274f57bc2")
    guardian = guardian.json()
    
    buzz = requests.get("https://newsapi.org/v1/articles?source=buzzfeed&sortBy=top&apiKey=6ef0dce6d16e45ffa1fdd01274f57bc2")
    buzz = buzz.json()
    
    ap = requests.get("https://newsapi.org/v1/articles?source=associated-press&sortBy=top&apiKey=6ef0dce6d16e45ffa1fdd01274f57bc2")
    ap = ap.json()
    
    abc = requests.get("https://newsapi.org/v1/articles?source=abc-news-au&sortBy=top&apiKey=6ef0dce6d16e45ffa1fdd01274f57bc2")
    abc = abc.json()
    
    bbcsport = requests.get("https://newsapi.org/v1/articles?source=bbc-sport&sortBy=top&apiKey=6ef0dce6d16e45ffa1fdd01274f57bc2")
    bbcsport = bbcsport.json()
    
    binsider = requests.get("https://newsapi.org/v1/articles?source=business-insider&sortBy=top&apiKey=6ef0dce6d16e45ffa1fdd01274f57bc2")
    binsider = binsider.json()
    
    eweekly = requests.get("https://newsapi.org/v1/articles?source=entertainment-weekly&sortBy=top&apiKey=6ef0dce6d16e45ffa1fdd01274f57bc2")
    eweekly = eweekly.json()
    
    ftimes = requests.get("https://newsapi.org/v1/articles?source=financial-times&sortBy=top&apiKey=6ef0dce6d16e45ffa1fdd01274f57bc2")
    ftimes = ftimes.json()
    
    mashable = requests.get("https://newsapi.org/v1/articles?source=mashable&sortBy=top&apiKey=6ef0dce6d16e45ffa1fdd01274f57bc2")
    mashable = mashable.json()
        
    """ combine articles from json sources """
    news = bbc['articles'] + nytimes['articles'] + google['articles'] + independent['articles'] + economist['articles'] \
    + guardian['articles'] + buzz['articles'] + ap['articles'] + abc['articles'] + bbcsport['articles'] + binsider['articles'] \
    + eweekly['articles'] + ftimes['articles'] + mashable['articles']
    
    
    """ sentiment analysis for good news """
    milk = request.form['milk']
    
    if milk == "chocolate":
       # instantiate analyser
        analyzer = Analyzer()
        for description in news[:]:
            if description['description'] is None:
                print("nonetype")
            else:
                score = analyzer.analyze(description['description'] + description['title'])
                if score < 3:
                    news.remove(description)
                else:
                    print('keep')
    elif milk == "skimmed":
        del news[::2]
        del news[::2]
        return news
    elif milk == "whole":
        del news[::2]
    return news