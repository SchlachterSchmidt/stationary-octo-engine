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

    ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

    S3_KEY = os.environ['S3_ACCESS_KEY_ID']
    S3_SECRET = os.environ['S3_SECRET_ACCESS_KEY']


class TestConfig(Config):
    """Config class for test environment."""

    SQLALCHEMY_DATABASE_URI = os.environ['TEST_DATABASE_URL']
    S3_BUCKET = os.environ['TEST_S3_BUCKET']
    S3_LOCATION = 'http://{}.s3.amazonaws.com/'.format(S3_BUCKET)


class DevConfig(Config):
    """Config class for dev environment."""

    SQLALCHEMY_DATABASE_URI = os.environ['DEV_DATABASE_URL']
    S3_BUCKET = os.environ['DEV_S3_BUCKET']
    S3_LOCATION = 'http://{}.s3.amazonaws.com/'.format(S3_BUCKET)


class PrdConfig(Config):
    """Config class for prod environment."""

    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ['PRD_DATABASE_URL']
    S3_BUCKET = os.environ['PRD_S3_BUCKET']
    S3_LOCATION = 'http://{}.s3.amazonaws.com/'.format(S3_BUCKET)


app_config = {
    'development': DevConfig,
    'testing': TestConfig,
    'production': PrdConfig,
}
