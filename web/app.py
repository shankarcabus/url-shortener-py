# -*- coding: utf-8 -*-

from flask.ext.assets import Environment, Bundle
from flask.ext.pymongo import PyMongo
from flask.ext.login import LoginManager
import math
import re
import config
import time

#----------------------------------------
# initialization
#----------------------------------------

app = Flask(__name__)
# app.debug = True
app.config.update(
    DEBUG = True
)

mongo = PyMongo(app)
env = Environment(app)

login_manager = LoginManager()
login_manager.init_app(app)

# filename = 'general'
# # output = 'gen/%s.'%filename + '%(version)s.min.css'
# output = 'gen/%s.min.css'%filename
# bundle = Bundle('less/general.less', filters='less, yui_css', output=output)
# env.register('%s_css'%filename, bundle)

# js = Bundle('js/jquery.js', 'js/teste.js', output='gen/packed.js')
# env.register('js_all', js)

# css = Bundle('css/general.less','css/reset.less', filters='less', output='gen/packed.css')
# env.register('css_all', css)

#----------------------------------------
# login
#----------------------------------------

# User class
class DbUser(object):
  """ Wraps User object for Flask-Login """

  def __init__(self, user):
    self._user = user

  def get_id(self):
    return unicode(self._user.id)

  def is_active(self):
    return self._user.enabled

  def is_anonymous(self):
    return False

  def is_authenticated(self):
    return True

@login_manager.user_loader
def load_user(userid):
  return mongo.db.users.find({'userid': userid}) or None

@app.route("/login", methods=["GET", "POST"])
def login():
  if request.method == "POST" and "email" in request.form:
    username = request.form["username"]

    # check MongoDB for the existence of the entered username
    user = mongo.db.users.find_one({'email': email})
    userid = int(user['userid'])

    # create User object/instance
    db_user = DbUser(user, userid, active=True)

    # if username entered matches database, log user in
    if authenticate(app.config['AUTH_SERVER'], username, password):
      # log user in,
      login_user(db_user)
      return url_for("index"))
    else:
      flash("Invalid username.")
  else:
    flash(u"Invalid login.")
return render_template("login.html")

#----------------------------------------
# controllers
#----------------------------------------

@app.route('/')
def index():

  urls = [
    {}
  ]
  components = {
    'list' : render_template('components/urls_list.html', urls=urls)
  }

  params = {
    'config': config,
    'STATIC_URL': config.STATIC_URL,
    'components': components
  }
  return render_template('index.html', **params)

@app.route('/save', methods=['POST'])
def save():
  url = request.form['url']

  if not is_url(url):
    abort(500)

  if not url.startswith('http'):
    url = "http://" + url

  timestamp = int(time.time()*1000) # Converts float timestamp (1371431252.882313) to integer with 3 decimal places (1371431252882)
  code = encode_time(timestamp)
  doc = {
    'url': url,
    'code': code,
    'user': {}
  }
  # Inserts a new doc
  mongo.db.urls.insert(doc)

  return url_for("redirect_url", code=code, _external=True)

@app.route('/<string:code>')
def redirect_url(code):
  # Gets
  doc_url = mongo.db.urls.find_one({'code': code})

  if doc_url:
    return redirect(doc_url['url'] , 301)

  return redirect(url_for("index"))

#----------------------------------------
# helpers
#----------------------------------------

def to_base(num, base):

  SYMBOLS = list("0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")

  # Base may not be greater than symbols neither less than 2
  if base > len(SYMBOLS) or base < 2:
    return False

  converted = ""
  # Using the method of successive divisions
  while num > 0:
    # Quotient of division
    quotient = math.floor(num/base)
    # Remainder of division
    remainder = num - (base * quotient)
    # Prepend the symbol
    converted = SYMBOLS[int(remainder)] + converted
    num = quotient;

  return converted

def encode_time(timestamp):
  base = 62
  return to_base(math.floor(timestamp), base)

def is_url(url):
  regex = ur"(https?:\/\/[^\s\(\)]+)|(w{3}(\.\w+){2,}((\/|\?)[^\s\(\)]*)?)|((((?:\b)\w{1,2}(?=\.))|[^w\W]{3}|\w{4,})(\.\w+)+(\/|\?)[^\s\(\)]*)"
  mat = re.search(regex, url, re.IGNORECASE)
  return mat

#----------------------------------------
# launch
#----------------------------------------

if __name__ == '__main__':
  app.run()
