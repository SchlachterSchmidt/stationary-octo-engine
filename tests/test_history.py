"""Basic Histroy endpoint unit test."""

import unittest
import json
import io
from app import create_app
from app.models import db
from base64 import b64encode


class HistoryTestCase(unittest.TestCase):
    """Class representing history unit tests."""

    def setUp(self):
        """Initialize app and set up test variables."""
        self.app = create_app(config_mode='testing')
        self.client = self.app.test_client()

        self.test_user = {'username': 'hansi',
                          'firstname': 'Hans',
                          'lastname': 'Gruber',
                          'email': 'hans.gruber@nakatomi.com',
                          'password': 'python'}

        self.b64_user_and_credentials = str(b64encode(b'hansi:python'))[2:-1]

        with self.app.app_context():
            db.create_all()

    def test_get_history_records_no_url_params(self):
        """Returns 200 and history collection."""
        # create test user
        userCreateResponse = self.create_test_user()
        # post a few images for classification, creating the history
        postResponses = []
        for i in range(5):
            response = self.post_image_for_classification()
            postResponses.append(response)

        # get history collection
        headers = dict(Authorization="Basic " + self.b64_user_and_credentials)
        getHistoryResponse = self.client.get('api/v0.1/classifier',
                                             headers=headers)

        # assert that test user was created and the history was returned
        self.assertEqual(userCreateResponse.status_code, 201)
        self.assertEqual(getHistoryResponse.status_code, 200)
        # assert that the response is as expected
        self.assertIn('link', str(getHistoryResponse.data))
        self.assertIn('test.jpg', str(getHistoryResponse.data))
        self.assertIn('predicted_label', str(getHistoryResponse.data))
        self.assertIn('taken_at', str(getHistoryResponse.data))

    def test_get_history_record_with_url_parameters(self):
        """Returns 200 and history collection."""
        # create test user
        userCreateResponse = self.create_test_user()
        # post a few images for classification, creating the history
        postResponses = []
        for i in range(5):
            response = self.post_image_for_classification()
            postResponses.append(response)

        # get history collection
        headers = dict(Authorization="Basic " + self.b64_user_and_credentials)
        getHistoryResponse = self.client.get(
                                'api/v0.1/classifier?limit=1&offset=2',
                                headers=headers)
        # assert that test user was created and the history was returned
        self.assertEqual(userCreateResponse.status_code, 201)
        self.assertEqual(getHistoryResponse.status_code, 200)
        # assert that the response is as expected
        self.assertIn('link', str(getHistoryResponse.data))
        self.assertIn('test.jpg', str(getHistoryResponse.data))
        self.assertIn('predicted_label', str(getHistoryResponse.data))
        self.assertIn('taken_at', str(getHistoryResponse.data))
        self.assertIn('"id": 3', str(getHistoryResponse.data))

    def test_get_history_record_not_found(self):
        """Returns 404 and 'record not found' message"""
        # create test user
        userCreateResponse = self.create_test_user()
        # get history collection
        headers = dict(Authorization="Basic " + self.b64_user_and_credentials)
        getHistoryResponse = self.client.get('api/v0.1/classifier',
                                             headers=headers)

        self.assertEqual(userCreateResponse.status_code, 201)
        self.assertEqual(getHistoryResponse.status_code, 404)
        self.assertIn('not found', str(getHistoryResponse.data))

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

    def post_image_for_classification(self):
        """Util method to post image to classifier."""
        with open('tests/static/test_img.jpg', 'rb') as image:
            headers = dict(Authorization="Basic " +
                           self.b64_user_and_credentials,
                           Content_type="multipart/form-data")
            # image data as byte stream, in 'data' field of request
            payload = dict(data=(io.BytesIO(image.read()), 'test.jpg'),
                           prev_score=5)

            postResponse = self.client.post('api/v0.1/classifier',
                                            headers=headers,
                                            data=payload)
            return postResponse


if __name__ == "__main__":
    unittest.main()
