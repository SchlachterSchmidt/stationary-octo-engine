"""Module contains all database models."""
from app import db


class User(db.Model):
    """User model."""

    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(64), index=True, nullable=False)
    lastname = db.Column(db.String(64), index=True, nullable=False)
    email = db.Column(db.String(64), index=True, nullable=False)
    username = db.Column(db.String(64), index=True, nullable=False)

    def __repr__(self):
        """User representation."""
        return '<user %r>' % (self.username)