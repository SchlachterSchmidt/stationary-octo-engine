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
        self.client = self.app.test_client

        self.test_user = {'username': 'hansi',
                          'firstname': 'Hans',
                          'lastname': 'Gruber',
                          'email': 'hans.gruber@nakatomi.com',
                          'password': 'python'}

        with self.app.app_context():
            db.create_all()

    def test_classify_jpg_image(self):
        """Test API can classify a provided image (POST request)."""

        # create test user to use in request
        createUser = self.client().post('api/v0.1/users',
                                        data=json.dumps(self.test_user),
                                        content_type='application/json')

        with open('tests/static/test_img.jpg', 'rb') as image:
            # base 64 encoded version of the username and password
            user_and_credentials = str(b64encode(b'hansi:python'))[2:-1]
            headers = dict(Authorization="Basic " + user_and_credentials,
                           Content_type="multipart/form-data")
            # image data as byte stream, in 'data' field of request
            payload = dict(data=(io.BytesIO(image.read()), 'test.jpg'))

            postResponse = self.client().post('api/v0.1/classifier',
                                              headers=headers,
                                              data=payload)

        self.assertEqual(createUser.status_code, 201)
        self.assertEqual(postResponse.status_code, 200)
        self.assertIn('filename', str(postResponse.data))
        self.assertIn('test.jpg', str(postResponse.data))
        self.assertIn('prediction', str(postResponse.data))
        self.assertIn('probabilities', str(postResponse.data))

    def test_classify_unsupported_file_type(self):
        """Test API refuses unsupported file type (POST request)."""
        # create test user to use in request
        createUser = self.client().post('api/v0.1/users',
                                        data=json.dumps(self.test_user),
                                        content_type='application/json')


        # TODO: post file extension not supported in config.py

        # assert user was created
        self.assertEqual(createUser.status_code, 201)

    def tearDown(self):
        """Teardown all initialized variables."""
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()


if __name__ == "__main__":
    unittest.main()
