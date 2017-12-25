"""Module containing API endpoints."""

from flask import make_response, jsonify, request, abort
from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

from app import app, db
from .models import User


@app.route('/api/v0.1/hello', methods=['GET'])
def hello():
    """Hello World API call."""
    return make_response(jsonify({'hello': 'world'}), 200)


@app.route('/api/v0.1/users', methods=['POST'])
def register_user():
    """Create a new user."""
    username = request.json.get('username')
    firstname = request.json.get('firstname')
    lastname = request.json.get('lastname')
    email = request.json.get('email')
    password = request.json.get('password')

    if username is None or firstname is None or lastname is None or email is None or password is None:
        abort(400, 'required parameter missing')

    if User.query.filter_by(username=username).first() is not None:
        abort(400, 'username already exists')

    user = User(
                username=username, firstname=firstname, lastname=lastname,
                email=email)

    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return make_response(jsonify({'username': user.username}), 201)


@app.route('/api/v0.1/users/<int:user_id>', methods=['GET'])
@auth.login_required
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


@app.errorhandler(400)
def bad_request(error):
    """Error handler to build 400 error in JSON"""
    return make_response(jsonify({'error': error.description}), 400)


@auth.verify_password
def verify_password(username, password):
    """Verify provided username / password pair against user record in db."""
    user = User.query.filter_by(username=username).first()
    if not user or not user.verify_password(password):
        return False
    return True
