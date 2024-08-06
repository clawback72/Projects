# EAST PITTSBURGH CYCLE RESOURCE
#### Video Demo: <https://youtu.be/9Spsby5xeEM>
#### Description:
East Pittsburgh Cycle Resource (EPGH Cycle) is a Flask based website that allows cyclists local to the eastern suburbs of Pittsburgh, PA to track their rides and compare their progress with their peers.  The website uses sqlite on the back end to track all data and employs Bootstrap 5 and Datatables on the front for full responsiveness, so it works great on mobile devices as well as desktop browsers.
### Files / Directories Included:
### /epgh_cycle - this is the root directory
- **app.py** - this is the flask application that controls all session handling, routing, database calls, and logic.
- **eastpgh.db** - this is the sqlite database that stores all data across three tables: users, log, and trails.
- **helpers.py** - this file houses a number of functions called from app.py that includes regex definitions, formatting definitions, and various functions.
- **requirements.txt** - list of packages required to run EPGH Cycle
### /flask_session - directory for handling temporary data relating to flask session
### /static - contains media for carousel, trails page and favicon.  Also houses local css files and JavaScript file
- **styles.css** - css file that contains custom definitions for navbar, carousel, and other bespoke page elements
- **table.css** - this is a custom table css provided by datatables.net - there were many conflicts with this service using their CDN links, so this is used in lieu.  Provides access to pagenation, row sorting, search, etc for most of the site tables.
- **script.js** - local JavaScript file that provides datatable definitions, time formatting, table row clicking functionality and delete confirmation through bootstrap modals.
### /templates - contains all html files used by site
- **add_ride.html** - This is a simple form page that allows users to add individual rides to the database.
- **bike_log.html** - This page provides a table view of all rides entered by the user sorted from most recent ride.  Datatables functionality provides pagenation, sorting and search capabilities.  Custom JavaScript allows the user to click on any row to access the "/view_ride" page for that specific ride.
- **index.html** - This is the main page the user is presented with upon login.  It greets the user by username and provides a table of the last ten most recent rides entered by all users.
- **layout.html** - This is the main layout page that all others extend from.  The head contains links for all required css and javascript CDNs for Bootstrap 5, Datatables and Jquery, as well as local pointers for css and js.  Functionality for the persistant carousel and navbar are also provided in this file, as well as flash functionality.
- **leaderboard.html** - This page contains two tables.  The first provides a table view of each individual users total distance, time, rides, average time and average MPH.  The second table contains much the same, but for the trails themselves.  Sortable columns allows individuals to measure their performance against other users across all categories, as well as see what trails are most popular in the area.
- **login.html** - simple page for user to enter their username and password
- **register.html** - users submit their desired username, password and email address to register for access to the site.  User names and email addresses are checked on the back end to ensure there is no conflict with existing accounts.
- **support.html** - simple support page that provides contact information.
- **trails.html** - page that lists the name, gives a brief description and a small photo of all trails currently tracked by the site.  This page is generated entirely from database query, which makes it extensible and trivial to add additional trails for tracking.
- **view_ride.html** - this page is reached by selecting a specific row  from the /bike_log table.  It provides a view of the specific entry, a button to return to the bike log, and a button to delete the entry if desired.  A confirmation button is provide via Bootstrap 5 modal to confirm deletion.
- **welcome.html** - brief greeting page that user is defaulted to if not logged in.  Provides basic greeting and instruction to register for access.
### Select Function Explanations
The site employs a number of functions and scripts - these are located primarily in helpers.py and script.js
- **usernameCheck(username)** - This function is called during user creation and checks via regex that the name subitted starts with a letter, is alphanumeric, and 5-15 characters in lenghth.  Returns a bool value.
- **emailCheck** - Also called during user creation to compare submitted email against a publicly available regex for conformity.  Returns a bool value.
- **getSecs(t)** - Converts ride time formatted in HH:MM:SS format to seconds.  Employs a flexible formula that can also handle MM:SS if provided.
- **getMph(d,s)** - Converts provided distance (d) and seconds (s) to MPH rounded to the nearest hundreth.
- **retTime(t)** - Formats seconds into HH:MM:SS format - primarily used in Jinja for display formatting in tables.
- **login_required(f)** - Login decorator that handles session routing - called each time user moves into a @login_required route.
- **format_time(time_input)** - JavaScript function that enforces time formating in HH:MM:SS on the "/add_ride" page.  Located in the scripts.js file.
- **other files in scripts.js** - Other functionality in this file not specified, in order are:  datables definitions, which call the format and the default sorting columns; a short script that manages the row clicking functionality of the "/bike_log" page; and the delete confirmation script for the Bootstrap 5 modal.
### Running the Program
EPGH Cycle is a fairly simple flask application.  See the requirements.txt file for all packages that are required.
To run locally, once in the /project directory, simply type 'flask run' to start the server and fetch the http link to access the site.
You can either create a new user to access the site, or use username "guest" password "guest" to just poke around with a default user account.
