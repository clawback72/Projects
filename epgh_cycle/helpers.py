import re

from flask import redirect, render_template, session
from functools import wraps
from datetime import timedelta

def usernameCheck(username):
    """
    Verify username is valid with regex

    https://www.makeuseof.com/regular-expressions-validate-user-account/
    """

    regex = re.compile("^[A-Za-z]\\w{4,14}$")

    # check username against regex and return bool
    if re.search(regex, username):
        return True
    else:
        return False

def emailCheck(email):
    """
    Verify email is valid with regex

    https://www.javatpoint.com/how-to-validated-email-address-in-python-with-regular-expression
    """

    regex = re.compile(r"([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\"([]!#-[^-~ \t]|(\\[\t -~]))+\")@([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\[[\t -Z^-~]*])")

    # check email against regex and return bool
    if re.fullmatch(regex, email):
        return True
    else:
        return False

def getSecs(t):
    """
    Convert ride time to seconds
    """
    seconds = sum(int(x) * 60 ** i for i, x in enumerate(reversed(t.split(':'))))
    return seconds

def getMph(d, s):
    """
    Convert distance and seconds to MPH
    """
    mph = float(d) / (s / 3600)
    return round(mph, 2)

def retTime(t):
    """
    Format seconds into HH:MM:SS
    """
    return (str(timedelta(seconds=t)))

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/welcome")
        return f(*args, **kwargs)
    return decorated_function

