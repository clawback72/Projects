from cs50 import SQL
from flask import Flask, redirect, render_template, request, session, flash, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import usernameCheck, emailCheck, getSecs, getMph, retTime, login_required

# Configure app
app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Setup SQLite databasse
db = SQL("sqlite:///eastpgh.db")


# after_request settings to clear cache
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response


@app.route("/")
@login_required
def index():
    """Show index page welcoming user and most recent ride info"""

    user_data = db.execute(
        "SELECT username FROM users WHERE id = (?)", session["user_id"]
    )
    name = user_data[0]["username"]

    ride_data = db.execute(
        "SELECT date_ride, loc, dist, time, mph, username FROM log JOIN users ON log.id = users.id ORDER BY date_ride DESC LIMIT 10"
    )

    return render_template(
        "index.html", name=name, ride_data=ride_data, retTime=retTime
    )


@app.route("/welcome")
def welcome():
    return render_template("welcome.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    # forget any user_id
    session.clear()

    # check if route via POST
    if request.method == "POST":
        # Make sure username submitted
        if not request.form.get("username"):
            flash("Must provide username.", "warning")
            return render_template("register.html")

        # Make sure username valid
        elif not usernameCheck(request.form.get("username")):
            flash(
                "Invalid username: start with letter, alphanumeric, 5-15 char",
                "warning",
            )
            return render_template("register.html")

        # Make sure password submitted
        elif not request.form.get("password"):
            flash("Must provide password.", "warning")
            return render_template("register.html")

        # Make sure password and confirmation match
        elif request.form.get("password") != request.form.get("confirm_password"):
            flash("Passwords do not match.", "warning")
            return render_template("register.html")

        # Make sure email is provided
        elif not request.form.get("email"):
            flash("Must provide email address.", "warning")
            return render_template("register.html")

        # Make sure email addresses match
        elif request.form.get("email") != request.form.get("confirm_email"):
            flash("email confirmation does not match", "warning")
            return render_template("register.html")

        # Make sure email address is valid
        elif not emailCheck(request.form.get("email")):
            flash("email address invalid", "warning")
            return render_template("register.html")

        # Make sure username does not exist
        rows = db.execute("SELECT * FROM users")

        for row in rows:
            if row["username"] == request.form.get("username"):
                flash("Username taken", "warning")
                return render_template("register.html")

        # Data passes checks - create password hash and create user in db
        passhash = generate_password_hash(request.form.get("password"))

        db.execute(
            "INSERT INTO users (username, hash, email) VALUES (?,?,?)",
            request.form.get("username"),
            passhash,
            request.form.get("email"),
        )

        flash("User created!")
        return render_template("login.html")

    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    # User reached via POST
    if request.method == "POST":
        # Check for username
        if not request.form.get("username"):
            flash("Must provide username", "warning")
            return render_template("login.html")

        # Check for password
        elif not request.form.get("password"):
            flash("Must provide password", "warning")
            return render_template("login.html")

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Check credentials
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            flash("Invalid username and/or password", "warning")
            return render_template("login.html")

        # create session for user
        session["user_id"] = rows[0]["id"]

        # Redirect to homepage
        return redirect("/")

    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    # Clear user_id
    session.clear()

    flash("Successfully logged out", "success")
    return redirect("/")


@app.route("/add_ride", methods=["GET", "POST"])
@login_required
def add_ride():
    trails = db.execute("SELECT s_name FROM trails ORDER BY s_name")

    # Render page if arrived by "POST"
    if request.method == "POST":
        # check values entered are valid
        if not request.form.get("ride_date"):
            flash("Ride date required", "warning")
            return redirect("/add_ride")

        elif request.form.get("trail") == "Select Trail":
            flash("Please select trail from menu", "warning")
            return redirect("/add_ride")

        elif not request.form.get("distance"):
            flash("Distance travelled required", "warning")
            return redirect("/add_ride")

        elif not request.form.get("time"):
            flash("Time of ride required", "warning")
            return redirect("/add_ride")

        # Calculate seconds and MPH
        seconds = getSecs(request.form.get("time"))

        mph = getMph(request.form.get("distance"), seconds)

        # Add ride into log table
        db.execute(
            "INSERT INTO log (id, date_ride, loc, dist, time, mph, note) VALUES (?,?,?,?,?,?,?)",
            session["user_id"],
            request.form.get("ride_date"),
            request.form.get("trail"),
            request.form.get("distance"),
            seconds,
            mph,
            request.form.get("note"),
        )

        # Flash that ride has been added and redirect user
        flash("Ride data added!", "success")
        return render_template("add_ride.html", trails=trails)

    # render page when arrive through "GET"
    else:
        return render_template("add_ride.html", trails=trails)


@app.route("/bike_log", methods=["GET", "POST"])
@login_required
def bike_log():

    # POST method placeholder
    if request.method == "POST":
        pass

    # GET method
    else:
        ride_data = db.execute(
            "SELECT ride_id, date_ride, loc, dist, time, mph, username FROM log JOIN users ON log.id = users.id WHERE log.id = ? ORDER BY date_ride DESC LIMIT 100",
            session["user_id"],
        )

        # make sure user has data - if not render bike log with ride_data = "empty"
        if not ride_data:
            return render_template(
                "bike_log.html", ride_data="empty"
            )

        return render_template(
            "bike_log.html", ride_data=ride_data, retTime=retTime
        )


@app.route("/leaderboard", methods=["GET", "POST"])
@login_required
def leaderboard():
    # render page when arrive through "POST"
    if request.method == "POST":
        pass

    # render page when arrive through "GET"
    else:
        # User Leaderboard
        # get list of all names
        names = db.execute("SELECT id, username FROM users")

        # create dict for user statistics
        stats = []

        # query for each users data
        for name in names:
            cyclist = {}

            data = db.execute(
                "SELECT SUM(dist), SUM(time), COUNT(ride_id) FROM log WHERE id = (?)",
                name["id"],
            )

            # check that user has data to add - if yes, create dictionary for user and add to stats list - if no, skip
            if data[0]["SUM(dist)"]:
                cyclist = {
                "name": name["username"],
                "distance": round(data[0]["SUM(dist)"], 2),
                "time": data[0]["SUM(time)"],
                "rides": data[0]["COUNT(ride_id)"],
                "avg_time": int((data[0]["SUM(time)"]) / data[0]["COUNT(ride_id)"]),
                "avg_mph": getMph(round(data[0]["SUM(dist)"], 2), data[0]["SUM(time)"]),
                }
                stats.append(cyclist)

        # Trail Leaderboard
        # get list of all trails
        t_names = db.execute("SELECT s_name FROM trails")

        # create dict for trail stats
        t_stats = []

        # query for each trails data
        for t_name in t_names:
            trail = {}

            data = db.execute(
                "SELECT SUM(dist), SUM(time), COUNT(ride_id), COUNT(DISTINCT id) FROM log WHERE loc = (?)",
                t_name["s_name"]
            )

            trail = {
                "name": t_name["s_name"],
                "distance": round(data[0]["SUM(dist)"], 2),
                "time": data[0]["SUM(time)"],
                "rides": data[0]["COUNT(ride_id)"],
                "avg_time": int((data[0]["SUM(time)"]) / data[0]["COUNT(ride_id)"]),
                "unique": data[0]["COUNT(DISTINCT id)"],
            }
            t_stats.append(trail)

        return render_template("leaderboard.html", stats=stats, t_stats=t_stats, retTime=retTime)


@app.route("/trails")
@login_required
def trails():
    # get trail information
    trails = db.execute("SELECT * FROM trails ORDER BY l_name")

    return render_template("trails.html", trails=trails)


@app.route("/view_ride", methods=["GET", "POST"])
@login_required
def view_ride():
    if request.method == "POST":
        if request.form.get("return"):
            return redirect("/bike_log")
        elif request.get_json().get("ride_id"):
            delete_value = request.get_json().get("ride_id")

            d_row = db.execute("SELECT id FROM log WHERE ride_id=(?)", delete_value)

            if d_row[0]["id"] == session["user_id"]:
                db.execute("DELETE FROM log WHERE ride_id=(?)", delete_value)
                return jsonify({"flash": "Ride Deleted"})
            else:
                flash("Permission Denied", "warning")
                return render_template("index.html")

    else:
        ride_id = request.args.get("id")

        ride = db.execute(
            "SELECT id, date_log, date_ride, loc, dist, time, mph, note FROM log WHERE ride_id=(?)",
            ride_id,
        )

        if ride[0]["id"] == session["user_id"]:
            return render_template(
                "view_ride.html", ride=ride, ride_id=ride_id, retTime=retTime
            )
        else:
            flash("Permission Denied", "warning")
            return render_template("index.html")


@app.route("/support")
@login_required
def support():
    return render_template("support.html")
