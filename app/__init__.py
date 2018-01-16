"""REST API prividing access to webserver resources for mobile agents."""

from flask import Flask
from config import app_config


def create_app(config_mode='development'):
    """Wrapping app creation in factory according to specified config."""
    # create app and load config
    app = Flask(__name__)
    app.config.from_object(app_config[config_mode])

    # register API blueprint defined in ./api/__init__.py
    from .api import api
    app.register_blueprint(api)

    from .models import db

    # register app with SQLAlchemy
    db.app = app
    db.init_app(app)

    if config_mode is 'development':
        print(app.config)

    return app
