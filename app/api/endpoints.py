"""Module containing API endpoints."""

from flask import make_response, jsonify, request, abort, current_app
from flask_httpauth import HTTPBasicAuth
from werkzeug.utils import secure_filename


from . import api
from ..models import User, ImageRef
from ..classifier import Classifier


classifier = Classifier()
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
                                  'username': user.username}), 201)


@api.route('/api/v0.1/users/<int:user_id>', methods=['GET'])
@auth.login_required
def get_user(user_id):
    """Return a single user by ID."""
    user = User.query.get_or_404(user_id)
    requester = User.query.filter_by(
        username=request.authorization.username).first()
    # if user making the request is not the same user that is being updated:
    if user.id is not requester.id:
        abort(401, 'you do not have access to this')
    return make_response(jsonify({'id': user.id,
                                  'firstname': user.firstname,
                                  'lastname': user.lastname,
                                  'email': user.email,
                                  'username': user.username}), 200)


@api.route('/api/v0.1/users/<int:user_id>', methods=['PUT'])
@auth.login_required
def update_user(user_id):
    """Update a single user by ID."""
    user = User.query.get_or_404(user_id)
    requester = User.query.filter_by(
        username=request.authorization.username).first()
    # if user making the request is not the same user that is being updated:
    if user.id is not requester.id:
        abort(401, 'you do not have access to this')

    payload = request.get_json()

    # checking piece by piece if the user can be updated to the payload:
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

    user.username = payload['username']
    user.email = payload['email']
    user.firstname = payload['firstname']
    user.lastname = payload['lastname']
    user.save()

    return make_response(jsonify({'id': user.id,
                                  'firstname': user.firstname,
                                  'lastname': user.lastname,
                                  'email': user.email,
                                  'username': user.username}))



#                            #
#    CLASSIFIER API BLOCK    #
#                            #

@api.route('/api/v0.1/classifier', methods=['POST'])
@auth.login_required
def classify():
    """Accept image file and return classification."""
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

    probabilities, prediction = classifier.classify(image)

    image_ref = ImageRef(image=image,
                         fileStoreObj=fileStoreObj,
                         prediction=prediction,
                         probabilities=probabilities,
                         username=request.authorization.username)
    image_ref.save()

    return make_response(jsonify({'filename': fileStoreObj.filename,
                                  'prediction': prediction,
                                  'probabilities': probabilities}), 200)


@api.route('/api/v0.1/classifier', methods=['GET'])
@auth.login_required
def get_results():
    limit = request.args.get('limit', 50)
    offset = request.args.get('offset', 0)

    requester = User.query.filter_by(
        username=request.authorization.username).first()
    results = ImageRef.query.filter_by(
        user_id=requester.id).limit(limit).offset(offset).all()

    if not results:
        abort(404)

    json_results = []
    for result in results:
        d = {'id': result.id,
             'link': result.link,
             'predicted_label': result.predicted_label,
             'taken_at' :result.taken_at}
        json_results.append(d)

    return make_response(jsonify(results=json_results), 200)


#                           #
#    UTILS AND CALLBACKS    #
#                           #

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
    return make_response(jsonify({'error': 'not found'}), 404)


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
    return make_response(jsonify({'error': 'not authorized'}), 401)


def allowed_file_type(filename):
    """Check if file type that is being posted is permitted."""
    app = current_app._get_current_object()
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']
