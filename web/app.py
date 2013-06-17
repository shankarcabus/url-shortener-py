from flask import Flask, render_template, request, redirect, url_for, abort
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
app.config.update(
    DEBUG = True
)

mongo = PyMongo(app)
env = Environment(app)

#----------------------------------------
# login
#----------------------------------------

@login_manager.user_loader
def load_user(userid):
  return mongo.db.users.find({'id': userid}) or None

@app.route("/login", methods=["GET", "POST"])
def login():
  form = LoginForm()
  if form.validate_on_submit():
    # login and validate the user...
    login_user(user)
    flas............h("Logged in successfully.")
    return redirect(request.args.get("next") or url_for("index"))
  return render_template("login.html", form=form)

#----------------------------------------
# controllers
#----------------------------------------

@app.route('/')
def index():

  components = {
    'list' : render_template('components/urls_list.html')
  }

  # TOFIX: remove config from here
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

  mongo.db.urls.insert(doc)

  return url_for("redirect_url", code=code, _external=True)

@app.route('/<string:code>')
def redirect_url(code):
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
