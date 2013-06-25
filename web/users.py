# -*- coding: utf-8 -*-

import time
import datetime
import logging

import flask
import simplejson as json

from flask import request, redirect, url_for, utils

_log = logging.getLogger(__name__)

def set_current_user(uid, response=None, keep_me=True):

  config = flask.current_app.config
  cookie_value = utils.encode_value(config['COOKIE_NAME'], uid)
  if response is None:
    response = redirect(url_for('perfil.index'))

  expires = None
  if keep_me:
    # get expires cookie configuration
    now = datetime.datetime.now()
    lifetime = config['PERMANENT_SESSION_LIFETIME']
    if isinstance(lifetime, int):
      expires = now + datetime.timedelta(seconds=lifetime)
    elif isinstance(lifetime, datetime.timedelta):
      expires = now + lifetime

    # We used the timestamp since werkzeug set cookie expires formated as GMT
    expires = long(time.mktime(expires.timetuple()))
  response.set_cookie(config['COOKIE_NAME'], value=cookie_value, domain=config['SESSION_COOKIE_DOMAIN'], expires=expires)
  return response

def get_current_user():
  """Gets the logged user"""
  return getattr(flask.g, 'user', None)


def load_current_user():
  """ Load the current user data. """

  cookie_name = flask.current_app.config['COOKIE_NAME']
  flask.g.user = None
  if cookie_name in request.cookies:
    cookie_value = utils.decode_value(cookie_name, request.cookies[cookie_name])
    try:
      flask.g.user = _build_session_user(**json.loads(cookie_value))
    except Exception as e:
      # Ignore invalid user cookie and overwrite on the next login.
      _log.error('Can not load the user session: %s\ncookie_value: %s' % (str(e), cookie_value))

