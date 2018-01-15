"""REST API prividing access to webserver resources for mobile agents."""

from flask import Flask
from config import app_config
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app(app_config_class):
    """Wrapping app creation in factory according to specified config."""

    # create app and load config
    app = Flask(__name__)
    app.config.from_object(app_config[app_config_class])

    # register API blueprint defined in ./api/__init__.py
    from .api import api
    app.register_blueprint(api)

    from .model import db

    # register app with SQLAlchemy
    db.app = app
    db.init_app(app)

    print(app.config)

    return app
