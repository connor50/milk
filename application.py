from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import gettempdir
import time, calendar, requests, re
from analyzer import Analyzer
from flask_mail import Mail, Message

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

# establish database
db = SQL("sqlite:///milk.db")

# shhhh secret key
app.secret_key = 'F12Zr47j\3yX R~X@H!jmM]Lwf/,?KT'

""" email setup """
app.config.update(
	DEBUG=True,
	#EMAIL SETTINGS
	MAIL_SERVER='smtp.gmail.com',
	MAIL_PORT=465,
	MAIL_USE_SSL=True,
	MAIL_USERNAME = 'deliver.milk.now@gmail.com',
	MAIL_PASSWORD = 'delivered')

# instantiate mail instance.
mail = Mail(app)

# for every user in the database, go and send email.
db = SQL("sqlite:///milk.db")

emaillist = db.execute("SELECT email, milk FROM users")

#defined in app context to avoid runtime error.
def send_email():
    with app.app_context():
        for user in emaillist:
            email = user['email']
            milk = user['milk']
            msg = Message("Milk is here.",
            sender="deliver.milk.now@gmail.com",
            recipients=[email])
            news = getnews(milk)
            msg.body = 'hello'
            msg.html = render_template("email_" + str(milk) +".html", milk=milk, news=news)
            mail.send(msg)

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

    """ clean up article issues """
    for description in news[:]:
        if description['description'] is None:
            print("nonetype")
            news.remove(description)

    """ sentiment analysis for good news """

    if milk == "chocolate":
       # instantiate analyser
        analyzer = Analyzer()
        for description in news[:]:
            score = analyzer.analyze(description['description'] + description['title'])
            if score < 3:
                news.remove(description)

    elif milk == "skimmed":
        # skim the fat. (get rid of some articles from each source)
        del news[::2]
        del news[::2]
        return news
    elif milk == "whole":
        # similar concept here to avoid overwhelming user with news.
        del news[::2]
    return news

@app.route("/", methods=["GET", "POST"])
def index():
    """ this checks to see last time email has been sent and then if > 24hrs, it sends email"""
    if request.method == "GET":
        # get time from file
        f = open('date.txt', 'r+')
        lastemail = f.read()
        # get today time
        currenttime = calendar.timegm(time.gmtime())
        # if today time - this time is morethan 24 hours (in seconds)
        if (int(currenttime) - int(lastemail) > 86400):
            send_email()
            # update time in file
            f.seek(0)
            f.write(str(currenttime))
            f.truncate()
            f.close()
        else:
            f.close()

    if request.method == "POST":
        # if picture is clicked, store current milk type in session.
        session["milk"] = request.form['milk']

        # get news data for this type of milk
        news = getnews(session["milk"])

        # renders appropriate template based on type of milk.
        if session["milk"] == "chocolate":
            return render_template("chocolate.html", milk=session['milk'], news=news)
        elif session["milk"] == "skimmed":
            return render_template("skimmed.html", milk=session['milk'], news=news)
        elif session["milk"] == "whole":
            return render_template("whole.html", milk=session['milk'], news=news)
    else:
        return render_template("index.html")

@app.route("/deliver", methods=["GET", "POST"])
def deliver():
    if request.method == "POST":
        # if email field is empty return register field again.
        if not request.form.get("email"):
            return render_template("register.html")
        # check if email is in email format.
        elif re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", request.form.get("email")):
            # check if email already exists:
            if db.execute("SELECT * FROM users WHERE email = :email", email=request.form.get("email")):
                # return error that email has already been registered.
                error = "You already get milk delivered. Enter another address for more milk."
                return render_template("register.html", error=error)
            elif not request.form.get("milktype"):
                # milktype not selected.
                error = "select a milktype"
                return render_template("register.html", error=error)
            else:
                # if all clear then insert user into database.
                db.execute("INSERT INTO users (email, milk) VALUES(:email,:milk)",
        email=request.form["email"], milk=request.form.get("milktype"))
            return render_template("success.html")
        else:
            # else email address is not valid, get them to retur.
            error = "Please enter a valid email address"
            return render_template("register.html", error=error )
    else:
        return render_template("register.html")
