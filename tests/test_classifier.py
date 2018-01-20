"""Basic Classifier endpoint unit test."""

import unittest
import json
import io
from base64 import b64encode
from app import create_app
from app.models import db


class ClassifierTestCase(unittest.TestCase):
    """Class representing classifier unit tests."""

    def setUp(self):
        """Initialize app and set up test variables."""
        self.app = create_app(config_mode='testing')
        self.client = self.app.test_client()

        self.test_user = {'username': 'hansi',
                          'firstname': 'Hans',
                          'lastname': 'Gruber',
                          'email': 'hans.gruber@nakatomi.com',
                          'password': 'python'}

        # base 64 encoded version of the username and password
        self.b64_user_and_credentials = str(b64encode(b'hansi:python'))[2:-1]

        with self.app.app_context():
            db.create_all()

    def test_classify_jpg_image(self):
        """Returns 200 and classification result."""

        # create test user to use in request
        createUser = self.create_test_user()
        postResponse = self.post_image_for_classification('supported')

        # assert user was created
        self.assertEqual(createUser.status_code, 201)
        # assert response code and message are as expected
        self.assertEqual(postResponse.status_code, 200)
        self.assertIn('filename', str(postResponse.data))
        self.assertIn('test_img.jpg', str(postResponse.data))
        self.assertIn('prediction', str(postResponse.data))
        self.assertIn('probabilities', str(postResponse.data))

    def test_classify_fails_with_unsupported_file_type(self):
        """Returns 400 and 'illegal file type' if type is not supported"""

        # create test user to use in request
        createUser = self.create_test_user()
        postResponse = self.post_image_for_classification('not_supported')

        # assert user was created
        self.assertEqual(createUser.status_code, 201)
        # assert response code and message are as expected
        self.assertEqual(postResponse.status_code, 400)
        self.assertIn('illegal file type', str(postResponse.data))

    def test_classify_illegal_file_name_is_sanitized(self):
        """Returns 200 and sanitized file name if name is illegal"""

        # create test user to use in request
        createUser = self.create_test_user()
        postResponse = self.post_image_for_classification('illegal_file')

        # assert user was created
        self.assertEqual(createUser.status_code, 201)
        # assert response code and message are as expected
        self.assertEqual(postResponse.status_code, 200)
        self.assertIn('filename', str(postResponse.data))
        # assert that the file name now has underscore in it
        self.assertIn('illegal_file.jpg', str(postResponse.data))
        self.assertIn('prediction', str(postResponse.data))
        self.assertIn('probabilities', str(postResponse.data))

    def test_classify_fails_when_user_is_unauthorized(self):
        """Returns 401 and 'not authorized' if credentials are wrong"""

        postResponse = self.post_image_for_classification('supported')

        self.assertEqual(postResponse.status_code, 401)
        self.assertIn('not authorized', str(postResponse.data))

    def test_classify_fails_when_no_image_in_request(self):
        """Returns 400 and 'no file' if no image is provided"""

        # create test user to use in request
        createUser = self.create_test_user()

        headers = dict(Authorization="Basic " + self.b64_user_and_credentials,
                       Content_type="multipart/form-data")

        postResponse = self.client.post('api/v0.1/classifier',
                                              headers=headers)

        # assert user was created
        self.assertEqual(createUser.status_code, 201)
        self.assertEqual(postResponse.status_code, 400)
        self.assertIn('no file in request', str(postResponse.data))

#    def test_classify_fails_when_image_unreadable(self):
#        """Returns 400 and 'unable to read file' if image is not readable"""
#
#        # create test user to use in request
#        createUser = self.client.post('api/v0.1/users',
#                                        data=json.dumps(self.test_user),
#                                        content_type='application/json')
#
#        headers = dict(Authorization="Basic " + self.b64_user_and_credentials,
#                       Content_type="multipart/form-data")
#
#        payload = dict(data=('', 'test.jpg'))
#
#        postResponse = self.client.post('api/v0.1/classifier',
#                                          headers=headers,
#                                          data=payload)
#
#        # assert user was created
#        self.assertEqual(createUser.status_code, 201)
#        self.assertEqual(postResponse.status_code, 400)
#        self.assertIn('unable to read file', str(postResponse.data))

    def tearDown(self):
        """Teardown all initialized variables."""
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()

    def create_test_user(self):
        """Util method to create new test user."""
        res = self.client.post('api/v0.1/users',
                               data=json.dumps(self.test_user),
                               content_type='application/json')
        return res

    def post_image_for_classification(self, flag):
        """Util method to post image to classifier."""
        if flag is 'not_supported':
            path = 'tests/static/test_textfile.txt'
            name = 'test_textfile.txt'
        if flag is 'supported':
            path = 'tests/static/test_img.jpg'
            name = 'test_img.jpg'
        if flag is 'illegal_file':
            path = 'tests/static/test_img.jpg'
            name = 'illegal file.jpg'

        with open(path, 'rb') as image:
            headers = dict(Authorization="Basic " + self.b64_user_and_credentials,
                           Content_type="multipart/form-data")
            # image data as byte stream, in 'data' field of request
            payload = dict(data=(io.BytesIO(image.read()), name))

            postResponse = self.client.post('api/v0.1/classifier',
                                              headers=headers,
                                              data=payload)
            return postResponse


if __name__ == "__main__":
    unittest.main()
