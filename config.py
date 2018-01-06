"""Final project flask app config file."""
import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    """Config super class."""

    DEBUG = True
    TESTING = True
    CSRF_ENABLED = True
    SECRET_KEY = os.environ['SECRET_KEY']
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ['TEST_DATABASE_URL']

    ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


class TestConfig(Config):
    """Config class for test environment."""

    SQLALCHEMY_DATABASE_URI = os.environ['TEST_DATABASE_URL']


class PrdConfig(Config):
    """Config class for prod environment."""

    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ['PRD_DATABASE_URL']
