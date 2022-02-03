"""

Flask App (sessions key, run app, general configurations)
Endpoint paths
Control Panel endpoint
Error Handlers here?

"""
import os
from flask import Flask, send_from_directory, session, render_template
from src.web.auth import *
from src.web.event import *
from src.web.user import *
from src.web.payment import *
from src.web.events_list import *
from src import config
from src.use_cases.register import get_user_info

app = Flask('BetBeans')
app.register_blueprint(auth) # Register authentication endpoints
app.register_blueprint(event) # Register everything about the seller (sell/events)
app.register_blueprint(user) # Register additional user details
app.register_blueprint(payment) # Payment functionalities
app.register_blueprint(events_list)
app.secret_key = config.SECRET_KEY
app.config['ENV'] = 'development'
app.config['DEBUG'] = True
app.config['UPLOAD_FOLDER'] = 'templates/assets/img'
app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg', 'gif'])
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
# Set secret key for authenticated cookies

@app.route('/assets/<path:path>') #Study this and see what it does exactly
def send_static(path):
    curr_path = os.getcwd()
    return send_from_directory(os.path.join(curr_path, 'templates', 'assets'), path)

@app.route("/user/<path:filename>")
@requires_access_level(1)
def footer_pages(filename):
     if "user" in session:
          logged_in = True
          myname, credit = get_user_info(session['user'])
          user_id = get_user_id(session['user'])[0]
          clearance = get_user_from_id(user_id)[1]
     else:
          myname = ''
          credit = 0
          logged_in = False
          clearance = 0
          print(filename)
     return render_template(filename + '.html', is_logged_in=logged_in, clearance_level=clearance, myName=myname, credit=credit)

@app.errorhandler(404) #Exception instead of 404 for when its not specific
def ErrorPage_404(e):
     return render_template('Error404.html')

@app.errorhandler(500) #Exception instead of 404 for when its not specific
def ErrorPage_500(e):
     return render_template('Error500.html')

@app.route('/TheBrain')
@requires_access_level(2)
def control_panel():
     if "user" in session:
          logged_in = True
          myname, credit = get_user_info(session['user'])
          user_id = get_user_id(session['user'])[0]
          clearance = get_user_from_id(user_id)[1]
     else:
          myname = ''
          credit = 0
          logged_in = False
          clearance = 0

     return render_template('ControlPanel.html', is_logged_in=logged_in, clearance_level=clearance, myName=myname, credit=credit)

@app.route("/TheBrain/<path:filename>")
@requires_access_level(2)
def admin_path(filename):
     if "user" in session:
          logged_in = True
          myname, credit = get_user_info(session['user'])
          user_id = get_user_id(session['user'])[0]
          clearance = get_user_from_id(user_id)[1]
     else:
          myname = ''
          credit = 0
          logged_in = False
          clearance = 0
          print(filename)
     return render_template(filename + '.html', is_logged_in=logged_in, clearance_level=clearance, myName=myname, credit=credit)

@app.route("/TheBrain/ManageEvents/<path:filename>")
@requires_access_level(2)
def manage_events(filename):
     if "user" in session:
          logged_in = True
          myname, credit = get_user_info(session['user'])
          user_id = get_user_id(session['user'])[0]
          clearance = get_user_from_id(user_id)[1]
     else:
          myname = ''
          credit = 0
          logged_in = False
          clearance = 0
          print(filename)
     return render_template(filename + '.html', is_logged_in=logged_in, clearance_level=clearance, myName=myname, credit=credit)

    # Flask already assumes the artifacts are inside the template/ folder

if __name__ == "__main__":
    hostname = os.getenv('HOSTNAME')
    port = os.getenv('PORT')
    app.run(host=config.flask_host, port=port)  # This blocks here