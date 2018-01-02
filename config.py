"""Final project flask app config file."""
import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    """Config super class."""

    DEBUG = True
    TESTING = True
    CSRF_ENABLED = True
    SECRET_KEY = 'this-should-be-kept-secret'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']

    ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
