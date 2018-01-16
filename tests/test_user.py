"""Basic User endpoint unit test."""
import unittest
import json
from app import create_app
from app.models import db


class UserTestCase(unittest.TestCase):
    """Class representing user unit tests."""

    def setUp(self):
        """Initialize app and set up test variables."""
        self.app = create_app(config_mode='testing')
        self.client = self.app.test_client

        self.base_user = {'username': 'hansi',
                          'firstname': 'Hans',
                          'lastname': 'Gruber',
                          'email': 'hans.gruber@nakatomi.com',
                          'password': 'python'}

        self.dupe_name_user = {'username': 'hansi',
                               'firstname': 'Hans',
                               'lastname': 'Gruber',
                               'email': 'hans.gruber_dupe_name@nakatomi.com',
                               'password': 'python'}

        self.dupe_email_user = {'username': 'hansi_dupe_email',
                                'firstname': 'Hans',
                                'lastname': 'Gruber',
                                'email': 'hans.gruber@nakatomi.com',
                                'password': 'python'}

        with self.app.app_context():
            db.create_all()

    def test_user_create(self):
        """Test API can create a new user (POST request)."""
        res = self.client().post('api/v0.1/users',
                                 data=json.dumps(self.base_user),
                                 content_type='application/json')

        self.assertEqual(res.status_code, 201)
        self.assertIn(self.base_user['username'], str(res.data))

    def test_user_create_username_taken(self):
        """Test API create user failes if username is taken (POST request)."""
        resOne = self.client().post('api/v0.1/users',
                                    data=json.dumps(self.base_user),
                                    content_type='application/json')
        resTwo = self.client().post('api/v0.1/users',
                                    data=json.dumps(self.dupe_name_user),
                                    content_type='application/json')

        self.assertEqual(resOne.status_code, 201)
        self.assertEqual(resTwo.status_code, 400)
        self.assertIn('username already taken', str(resTwo.data))

    def test_user_create_email_taken(self):
        """Test API create user failes if email is taken (POST request)."""
        resOne = self.client().post('api/v0.1/users',
                                    data=json.dumps(self.base_user),
                                    content_type='application/json')
        resTwo = self.client().post('api/v0.1/users',
                                    data=json.dumps(self.dupe_email_user),
                                    content_type='application/json')

        self.assertEqual(resOne.status_code, 201)
        self.assertEqual(resTwo.status_code, 400)
        self.assertIn('email already taken', str(resTwo.data))

#    def test_user_update(self):
#        """Test API update user details (POST request)."""
#        resOne = self.client().post('api/v0.1/users',
#                                    data=json.dumps(self.base_user),
#                                    content_type='application/json')
#
#        resTwo = self.client().post('api/v0.1/users/%s'
#                                    % self.base_user["username"],
#                                    data=json.dumps(self.base_user),
#                                    content_type='application/json')
#
#        self.assertEqual(resOne.status_code, 201)
#        self.assertIn(self.base_user['username'], str(resOne.data))

    def tearDown(self):
        """Teardown all initialized variables."""
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()


if __name__ == "__main__":
    unittest.main()
