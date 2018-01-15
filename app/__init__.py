"""REST API prividing access to webserver resources for mobile agents."""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import app_config

db = SQLAlchemy()


def create_app(app_config_class):
    """Wrapping app creation according to specified config."""

    from app import endpoints, models

    app = Flask(__name__)
    app.config.from_object(app_config[app_config_class])
    print(app.config)
    db.init_app(app)

    return app
