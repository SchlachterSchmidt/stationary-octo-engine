"""Module contains all database models."""

from flask_sqlalchemy import SQLAlchemy
from passlib.apps import custom_app_context as pwd_context
from sqlalchemy.dialects.postgresql import JSON
import datetime

from .helpers.s3_helper import upload_file_to_s3

db = SQLAlchemy()


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

    def save(self):
        """Save user to DB. This includes create and update operations."""
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        """User representation."""
        return '<user %r>' % (self.username)


class ImageRef(db.Model):
    """Image references associated with a user."""

    __tablename__ = 'image_refs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), index=True, nullable=False)
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

    def __init__(self, image, prediction, probabilities, user, fileStoreObj):
        """Extract class variables from the provided params."""
        self.image = image
        self.fileStoreObj = fileStoreObj

        self.user_id = User.query.filter_by(username=user).first().id,
        self.predicted_label = prediction
        self.c0 = probabilities[0]
        self.c1 = probabilities[1]
        self.c2 = probabilities[2]
        self.c3 = probabilities[3]
        self.c4 = probabilities[4]
        self.c5 = probabilities[5]
        self.c6 = probabilities[6]
        self.c7 = probabilities[7]
        self.c8 = probabilities[8]
        self.c9 = probabilities[9]

    def save(self):
        """Saving image aata to S2, and image ref object to DB."""
        self.link = upload_file_to_s3(self.image, self.fileStoreObj)
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        """Image representation."""
        return self.link


class HistoryRecord(db.Model):
    """Stores attention history of a user in json."""

    __tablename__ = 'history_records'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), index=True, nullable=False)
    history = db.Column(JSON)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        """History representation."""
        return '<History object for user id: %d>' % (self.id)
