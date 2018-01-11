"""Module contains all database models."""
from app import db
from passlib.apps import custom_app_context as pwd_context
from sqlalchemy.dialects.postgresql import JSON
import datetime


class User(db.Model):
    """User model."""

    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(64), index=True, nullable=False)
    lastname = db.Column(db.String(64), index=True, nullable=False)
    email = db.Column(db.String(64), index=True, nullable=False, unique=True)
    username = db.Column(db.String(64),
                         index=True, nullable=False, unique=True)
    password_hash = db.Column(db.String(120), nullable=False)
    active = db.Column(db.Boolean, index=True, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    images = db.relationship('ImageRef', backref='user', lazy=True)
    history = db.relationship('HistoryRecord', backref='user', lazy=True)

    def hash_password(self, password):
        """Hash plain text user password and store."""
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        """Verify plain text user provided password against stored hash."""
        return pwd_context.verify(password, self.password_hash)

    def __repr__(self):
        """User representation."""
        return '<user %r>' % (self.username)


class ImageRef(db.Model):
    """Image references associated with a user."""

    __tablename__ = 'image_refs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('user.id'), index=True, nullable=False)
    link = db.Column(db.String(200), index=True, nullable=False)
    predicted_label = db.Column(db.String(10), index=True, nullable=False)
    taken_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    c0 = db.Column(db.Float)
    c1 = db.Column(db.Float)
    c2 = db.Column(db.Float)
    c3 = db.Column(db.Float)
    c4 = db.Column(db.Float)
    c5 = db.Column(db.Float)
    c6 = db.Column(db.Float)
    c7 = db.Column(db.Float)
    c8 = db.Column(db.Float)
    c9 = db.Column(db.Float)

    def __repr__(self):
        """Image representation."""
        return self.link


class HistoryRecord(db.Model):
    """Stores attention history of a user in json."""

    __tablename__ = 'history_records'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('user.id'), index=True, nullable=False)
    history = db.Column(JSON)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        """History representation."""
        return '<History object for user id: %d>' % (self.id)
