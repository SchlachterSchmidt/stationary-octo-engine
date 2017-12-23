"""Module containing API endpoints."""

from flask import make_response, jsonify

from app import app
from .models import User


@app.route('/api/v0.1/hello', methods=['GET'])
def hello():
    """Hello World API call."""
    return make_response(jsonify({'hello': 'world'}), 200)


@app.route('/api/v0.1/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Return a single user by ID."""
    user = User.query.get_or_404(user_id)
    return make_response(
        jsonify({'firstname': user.firstname, 'lastname': user.lastname,
                 'email': user.email, 'username': user.username}))


@app.errorhandler(404)
def not_found(error):
    """Error handler to build 404 in JSON."""
    return make_response(jsonify({'error': 'Not found'}), 404)
