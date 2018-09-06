import os

from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from timeago import format

from helpers import apology, login_required, goodread

# Configure application
app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")


# Import from CS50 PSET7 Finance app: Ensure responses aren't cached.
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Home page and books search"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Extract keywords
        q = request.form.get("q")

        # Ensure search keywords were submitted
        if not q:
            return apology("Search query not provided")

        # Adding % for SQL LIKE arguments

        rows = db.execute("""SELECT * FROM books WHERE (isbn ILIKE :q)
                          OR (title ILIKE :q) OR (author ILIKE :q)
                          ORDER BY year DESC LIMIT 25""",
                          {"q": "%" + q + "%"}).fetchall()

        # Redirect user to home page
        return render_template("index.html", books=rows, q=q)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("index.html")


@app.route("/book/<isbn>", methods=["GET", "POST"])
@login_required
def book(isbn):
    """Book details and review"""
    # Query book details by ISBN
    row = db.execute("SELECT * FROM books WHERE isbn = :isbn",
                     {"isbn": isbn}).fetchone()

    # Check if there is a book in books database
    if not row:
        return apology("didn't find a book for this ISBN")

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Extract user review and rating for this book
        review = request.form.get("review")
        userrating = request.form.get("rating")

        if not userrating:
            return apology("Please provide rating")

        # Save user review and rating to database
        db.execute(
            """INSERT INTO reviews (id_user, id_book, rating, review, time)
            VALUES (:id_user, :id_book, :rating, :review, :time)""",
            {"id_user": session["user_id"],
             "id_book": row["id"],
             "rating": userrating,
             "review": review,
             "time": datetime.now()
             })

        db.commit()

    # Query Goodreads for book reviews
    ratings = goodread(isbn)

    # Query our database for user reviews
    reviews = db.execute(
        """SELECT reviews.id_book, reviews.id_user,
           reviews.rating, reviews.review, reviews.time, users.username
           FROM reviews, users
           WHERE reviews.id_user = users.id
           AND reviews.id_book = :id_book""",
        {"id_book": row["id"]}).fetchall()

    # Check if user already reviewed this book (returns boolean)
    reviewed = any(r.id_user == session["user_id"] for r in reviews)

    return render_template("book.html", row=row, rating=ratings,
                           reviews=reviews, reviewed=reviewed,
                           format=format, datetime=datetime)


# Import from CS50 PSET7 Finance
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Extracting username and password
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Ensure username was submitted
        if not username:
            return apology("must provide username")

        # Ensure password was submitted
        elif not password:
            return apology("must provide password")

        # Ensure confirmation was submitted too
        elif not confirmation:
            return apology("must confirm password")

        # Ensure passwords matches
        elif password != confirmation:
            return apology("confirmation doesn't match")

        # Ensure username wasn't used already
        userid = db.execute("SELECT id FROM users WHERE username = :username",
                            {"username": username}).fetchone()

        if userid:
            return apology("try another username")

        # Add user to users database
        db.execute(
            "INSERT INTO users (username, hash) VALUES (:username, :hash)",
            {"username": username, "hash": generate_password_hash(password)})

        db.commit()

        # Checking new user id
        userid = db.execute("SELECT id FROM users WHERE username = :username",
                            {"username": username}).fetchone()

        # Remember which user has logged in
        session["user_id"] = userid[0]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET
    else:
        return render_template("register.html")


# Import from CS50 PSET7 Finance
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        # Ensure username was submitted
        if not username:
            return apology("must provide username")

        # Ensure password was submitted
        elif not password:
            return apology("must provide password")

        # Query database for username
        user = db.execute("SELECT * FROM users WHERE username = :username",
                          {"username": username}).fetchone()

        # Ensure username exists and password is correct
        if not user or not check_password_hash(user.hash, password):
            return apology("invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = user.id

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


# Import from CS50 PSET7 Finance
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")
