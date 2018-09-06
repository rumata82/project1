from flask import redirect, render_template, session
from functools import wraps
import requests

goodreadskey = "pbx1XtPnZ3i94x8NB40w"


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html",
                           top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def goodread(isbns):
    """
    Request Goodreads API for reviews count and average rating
    """

    res = requests.get("https://www.goodreads.com/book/review_counts.json",
                       params={"key": goodreadskey, "isbns": isbns})

    if res.status_code == 200:
        rating = {}
        rating["count"] = res.json()["books"][0]["work_ratings_count"]
        rating["average"] = res.json()["books"][0]["average_rating"]
        return rating

    else:
        return None
