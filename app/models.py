"""Module contains all database models."""
from app import db
from passlib.apps import custom_app_context as pwd_context

class User(db.Model):
    """User model."""

    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(64), index=True, nullable=False)
    lastname = db.Column(db.String(64), index=True, nullable=False)
    email = db.Column(db.String(64), index=True, nullable=False, unique=True)
    username = db.Column(db.String(64), index=True, nullable=False, unique=True)
    password_hash = db.Column(db.String(120), nullable=False)
    images = db.relationship('ImageLink', backref='Creator', lazy=True)

    def hash_password(self, password):
        """Hash plain text user password and store."""
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        """Verify plain text user provided password against stored hash."""
        return pwd_context.verify(password, self.password_hash)

    def __repr__(self):
        """User representation."""
        return '<user %r>' % (self.username)


class ImageLink(db.Model):
    """Link to images associated with a user."""

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('user.id'), index=True, nullable=False)
    link = db.Column(db.String(200), index=True, nullable=False)
    predicted_label = db.Column(db.String(10), index=True, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        """Image representation."""
        return self.link
