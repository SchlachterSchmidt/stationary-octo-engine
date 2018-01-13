"""REST API prividing access to webserver resources for mobile agents."""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config.from_object('config.DevConfig')
print(app.config)
db = SQLAlchemy(app)


from app import endpoints, models
