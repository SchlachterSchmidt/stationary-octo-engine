"""Module containing API endpoints."""

from . import api

from flask import make_response, jsonify, request, abort, current_app
from flask_httpauth import HTTPBasicAuth
from werkzeug.utils import secure_filename

import logging
from logging.handlers import RotatingFileHandler
from time import strftime
import traceback

from ..models import User, ImageRef
from ..classifier import Classifier
from ..helpers.aggregator import aggregate_score


classifier = Classifier()
auth = HTTPBasicAuth()

handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=3)
logger = logging.getLogger('__name__')
logger.setLevel(logging.ERROR)
logger.addHandler(handler)


#                            #
#    HELLO WORLD API CALL    #
#                            #

@api.route('/api/v0.1/health', methods=['GET'])
def hello():
    """Hello World API call."""
    return make_response(jsonify({'hello': 'world'}), 200)


#                               #
#     SESSIONS API ENDPOINT     #
#                               #

@api.route('/api/v0.1/login', methods=['POST'])
def login():
    """Log in an existing user"""
    if not verify_password(request.authorization.username,
                           request.authorization.password):
                           abort(401, 'Username or password not correct')
    user = User.query.filter_by(
        username=request.authorization.username).first()
    if not user.active == True:
        abort(401, 'User account deactivated')
    return make_response(jsonify({'id': user.id,
                                  'firstname': user.firstname,
                                  'lastname': user.lastname,
                                  'email': user.email,
                                  'username': user.username,
                                  'active': user.active}), 200)


#                       #
#    USERS API BLOCK    #
#                       #

@api.route('/api/v0.1/users', methods=['POST'])
def register_user():
    """Create a new user."""
    username = request.json.get('username')
    firstname = request.json.get('firstname')
    lastname = request.json.get('lastname')
    email = request.json.get('email')
    password = request.json.get('password')

    if username is None or \
       firstname is None or \
       lastname is None or \
       email is None or \
       password is None:
        abort(400, 'required parameter missing')

    if User.query.filter_by(username=username).first() is not None:
        abort(400, 'username already taken')

    if User.query.filter_by(email=email).first() is not None:
        abort(400, 'email already taken')

    user = User(username=username,
                firstname=firstname,
                lastname=lastname,
                email=email)

    user.hash_password(password)
    user.save()

    return make_response(jsonify({'id': user.id,
                                  'firstname': user.firstname,
                                  'lastname': user.lastname,
                                  'email': user.email,
                                  'username': user.username,
                                  'active': user.active}), 201)


@api.route('/api/v0.1/users/<int:user_id>', methods=['GET'])
@auth.login_required
def get_user(user_id):
    """Return a single user by ID."""
    user = User.query.get_or_404(user_id)
    requester = User.query.filter_by(
        username=request.authorization.username).first()
    # if user making the request is not the same user that is being retrieved:
    if user.id is not requester.id:
        abort(401, 'you do not have access to this')
    return make_response(jsonify({'id': user.id,
                                  'firstname': user.firstname,
                                  'lastname': user.lastname,
                                  'email': user.email,
                                  'username': user.username,
                                  'active': user.active}), 200)


@api.route('/api/v0.1/users/<int:user_id>', methods=['PUT'])
@auth.login_required
def update_user(user_id):
    """Update a single user by ID."""
    user = User.query.get_or_404(user_id)
    requester = User.query.filter_by(
        username=request.authorization.username).first()
    # if user making the request is not the same user that is being updated:
    if user.id is not requester.id:
        abort(401, 'you do not have access to this')

    payload = request.get_json()

    # checking piece by piece if the user can be updated to the payload:
    # user wants to update email address
    if user.email is not payload['email']:
        found = User.query.filter_by(email=payload['email']).first()
        if found is not None and user.id is not found.id:
            abort(400, 'email already taken')
    # user wants to update username
    if user.username is not payload['username']:
        found = User.query.filter_by(username=payload['username']).first()
        if found is not None and user.id is not found.id:
            abort(400, 'username already taken')
    # appears to be a bug in psycopg2 that necessitates conversion before
    # writing to DB
    if payload['active'] == 'False' or\
       payload['active'] == 'false' or\
       payload['active'] == False:
        user.active = False
    else:
        user.active = True

    user.username = payload['username']
    user.email = payload['email']
    user.firstname = payload['firstname']
    user.lastname = payload['lastname']

    if 'password' in payload:
        user.hash_password(payload['password'])
    user.save()

    return make_response(jsonify({'id': user.id,
                                  'firstname': user.firstname,
                                  'lastname': user.lastname,
                                  'email': user.email,
                                  'username': user.username,
                                  'active': user.active}))


#                            #
#    CLASSIFIER API BLOCK    #
#                            #

@api.route('/api/v0.1/classifier', methods=['POST'])
@auth.login_required
def classify():
    """Accept image file and return classification."""

    if 'prev_score' not in request.form:
        abort(400, 'need previous score')
    prev_score = float(request.form['prev_score'])

    if 'data' not in request.files:
        abort(400, 'no file in request')
    fileStoreObj = request.files['data']
    if not allowed_file_type(fileStoreObj.filename):
        abort(400, 'illegal file type')
    if fileStoreObj:
        fileStoreObj.filename = secure_filename(fileStoreObj.filename)
    else:
        abort(400, 'unable to read file')

    image = fileStoreObj.read()

    probabilities, prediction, confidence = classifier.classify(image)
    score = aggregate_score(prev_score, prediction, confidence)

    image_ref = ImageRef(image=image,
                         fileStoreObj=fileStoreObj,
                         prediction=prediction,
                         probabilities=probabilities,
                         username=request.authorization.username,
                         distraction_score=score)
    image_ref.save()

    return make_response(jsonify({'filename': fileStoreObj.filename,
                                  'prediction': prediction,
                                  'probabilities': probabilities,
                                  'score': score,
                                  'confidence': confidence}), 200)


@api.route('/api/v0.1/classifier', methods=['GET'])
@auth.login_required
def get_results():
    """Return collection of image classification results sorted by timestamp"""
    limit = request.args.get('limit', 50)
    offset = request.args.get('offset', 0)

    requester = User.query.filter_by(
        username=request.authorization.username).first()
    results = ImageRef.query.filter_by(user_id=requester.id).order_by(
        ImageRef.taken_at.asc()).limit(limit).offset(offset).all()

    if not results:
        abort(404, 'No records found')

    json_results = []
    for result in results:
        d = {'id': result.id,
             'link': result.link,
             'predicted_label': result.predicted_label,
             'taken_at': result.taken_at,
             'distraction_score': result.distraction_score}
        json_results.append(d)

    return make_response(jsonify(results=json_results), 200)


#                           #
#    UTILS AND CALLBACKS    #
#                           #

@api.before_request
def before_request():
    """Execute before calls to log incoming requests"""
    timestamp = strftime('[%Y-%b-%d %H:%M:%S]')
    logger.error('%s %s %s %s %s\n%s',
                 timestamp,
                 request.remote_addr,
                 request.method,
                 request.full_path,
                 request.environ.get('SERVER_PROTOCOL'),
                 request.get_data())


@api.errorhandler(400)
def bad_request(error):
    """Error handler to build 400 error in JSON."""
    return make_response(jsonify({'error': error.description}), 400)


@api.errorhandler(401)
def illegal_request(error):
    """Error handler to build 401 error thrown in the application in JSON."""
    return make_response(jsonify({'error': error.description}), 401)


@api.errorhandler(404)
def not_found(error):
    """Error handler to build 404 in JSON."""
    if error.description is None:
        error.description = 'Not found'
    return make_response(jsonify({'error': error.description}), 404)


@api.errorhandler(Exception)
def exceptions(e):
    """Handle and log exceptions"""
    timestamp = strftime('[%Y-%b-%d %H:%M:%S]')
    traceback = traceback.format_exc()
    logger.error('exception: %s %s %s %s %s 500 INTERNAL SERVER ERROR\n%s',
                 timestamp,
                 request.remote_addr,
                 request.method,
                 request.scheme,
                 request.full_path,
                 traceback)
    return make_response(jsonify({'error': 'Internal Server Error'}), 500)


@api.after_request
def after_request(response):
    """Execute after requests to log responses"""
    # This if statement avoids the duplication of registry in the log,
    # since that 500 is already logged via @api.errorhandler.
    if response.status_code != 500:
        timestamp = strftime('[%Y-%b-%d %H:%M:%S]')
        logger.error('%s %s %s %s\n%s',
                     timestamp,
                     request.remote_addr,
                     'HTTP/1.1',
                     response.status,
                     response.get_data())
    return response


@auth.verify_password
def verify_password(username, password):
    """Verify provided username / password pair against user record in db."""
    user = User.query.filter_by(username=username).first()
    if not user or not user.verify_password(password):
        return False
    return True


@auth.error_handler
def unauthorized():
    """Error handler to build 401 in JSON."""
    return make_response(jsonify({'error': 'Not authorized'}), 401)


def allowed_file_type(filename):
    """Check if file type that is being posted is permitted."""
    app = current_app._get_current_object()
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']
