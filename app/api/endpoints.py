"""Module containing API endpoints."""

from flask import make_response, jsonify, request, abort, current_app
from flask_httpauth import HTTPBasicAuth
from werkzeug.utils import secure_filename


from . import api
from ..models import User, db
from ..classifier import Classifier
from ..helpers.db_writer import DB_Writer


classifier = Classifier()
db_writer = DB_Writer()
auth = HTTPBasicAuth()


#                            #
#    HELLO WORLD API CALL    #
#                            #

@api.route('/api/v0.1/hello', methods=['GET'])
def hello():
    """Hello World API call."""
    return make_response(jsonify({'hello': 'world'}), 200)


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

    user = User(
                username=username, firstname=firstname, lastname=lastname,
                email=email)

    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return make_response(jsonify({'username': user.username}), 201)


@api.route('/api/v0.1/users/<int:user_id>', methods=['GET'])
@auth.login_required
def get_user(user_id):
    """Return a single user by ID."""
    user = User.query.get_or_404(user_id)
    return make_response(
        jsonify({'firstname': user.firstname, 'lastname': user.lastname,
                 'email': user.email, 'username': user.username}))


#                            #
#    CLASSIFIER API BLOCK    #
#                            #

@api.route('/api/v0.1/classifier', methods=['POST'])
@auth.login_required
def classify():
    """Accept image file and return classification."""
    if 'data' not in request.files:
        abort(400, 'no file to classify provided')
    fileStoreObj = request.files['data']
    if not allowed_file_type(fileStoreObj.filename):
        abort(400, 'illegal file type')
    if fileStoreObj:
        fileStoreObj.filename = secure_filename(fileStoreObj.filename)
    else:
        abort(400, 'unable to read file from request')

    image = fileStoreObj.read()

    probabilities, prediction = classifier.classify(image)

    db_writer.write(image, fileStoreObj, prediction, probabilities,
                    request.authorization.username)

    return make_response(jsonify({'filename': fileStoreObj.filename,
                                  'prediction': prediction,
                                  'probabilities': probabilities}), 200)


#                           #
#    UTILS AND CALLBACKS    #
#                           #

@api.errorhandler(404)
def not_found(error):
    """Error handler to build 404 in JSON."""
    return make_response(jsonify({'error': 'Not found'}), 404)


@api.errorhandler(400)
def bad_request(error):
    """Error handler to build 400 error in JSON."""
    return make_response(jsonify({'error': error.description}), 400)


@auth.verify_password
def verify_password(username, password):
    """Verify provided username / password pair against user record in db."""
    user = User.query.filter_by(username=username).first()
    if not user or not user.verify_password(password):
        return False
    return True


def allowed_file_type(filename):
    """Check if file type that is being posted is permitted."""
    app = current_app._get_current_object()
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']
