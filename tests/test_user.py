"""Basic User endpoint unit test."""

import unittest
import json
from base64 import b64encode
from app import create_app
from app.models import db


class UserTestCase(unittest.TestCase):
    """Class representing user unit tests."""

    def setUp(self):
        """Initialize app and set up test variables."""
        self.app = create_app(config_mode='testing')
        self.client = self.app.test_client()

        self.user_one = {'username': 'hansi',
                         'firstname': 'Hans',
                         'lastname': 'Gruber',
                         'email': 'hans.gruber@nakatomi.com',
                         'password': 'python'}

        self.user_two = {'username': 'johnboy',
                         'firstname': 'John',
                         'lastname': 'McClane',
                         'email': 'john.mcclane@nypd.com',
                         'password': 'yippykayay'}

        self.b64_user_one_credentials = str(b64encode(b'hansi:python'))[2:-1]

        with self.app.app_context():
            db.create_all()

    def test_user_create(self):
        """Return 200 and user details."""
        res = self.client.post('api/v0.1/users',
                               data=json.dumps(self.user_one),
                               content_type='application/json')

        self.assertEqual(res.status_code, 201)
        self.assertIn(self.user_one['username'], str(res.data))

    def test_user_create_username_taken(self):
        """Return 400 and 'username already taken' if username is taken."""
        # create first test user
        userOneRes = self.client.post('api/v0.1/users',
                                      data=json.dumps(self.user_one),
                                      content_type='application/json')

        # set email of second test user to username in use and try to create
        self.user_two['username'] = self.user_one['username']
        userTwoRes = self.client.post('api/v0.1/users',
                                      data=json.dumps(self.user_two),
                                      content_type='application/json')

        self.assertEqual(userOneRes.status_code, 201)
        self.assertEqual(userTwoRes.status_code, 400)
        self.assertIn('username already taken', str(userTwoRes.data))

    def test_user_create_email_taken(self):
        """Return 400 and 'email already taken' if email is taken."""
        # create first test user
        userOneRes = self.client.post('api/v0.1/users',
                                      data=json.dumps(self.user_one),
                                      content_type='application/json')

        # set user two email to address already in use and try to create
        self.user_two['email'] = self.user_one['email']
        userTwoRes = self.client.post('api/v0.1/users',
                                      data=json.dumps(self.user_two),
                                      content_type='application/json')

        self.assertEqual(userOneRes.status_code, 201)
        self.assertEqual(userTwoRes.status_code, 400)
        self.assertIn('email already taken', str(userTwoRes.data))

    def test_user_update_name(self):
        """Return 200 and updated user details."""
        # construct authorization header
        headers = dict(Authorization="Basic " + self.b64_user_one_credentials)

        # create test user
        createUserRes = self.client.post('api/v0.1/users',
                                         data=json.dumps(self.user_one),
                                         content_type='application/json')

        # get ID of new user, update user dict, and put request
        user_id = json.loads(createUserRes.get_data(as_text=True))['id']
        self.user_one['firstname'] = 'Hans_updated'
        self.user_one['lastname'] = 'Gruber_updated'
        updateUserRes = self.client.put('api/v0.1/users/%s'
                                        % user_id,
                                        data=json.dumps(self.user_one),
                                        headers=headers,
                                        content_type='application/json')

        self.assertEqual(createUserRes.status_code, 201)
        self.assertEqual(updateUserRes.status_code, 200)
        self.assertIn('Hans_updated', str(updateUserRes.data))

    def test_user_update_fails_when_email_taken(self):
        """Return 400 when updating user email address in use."""
        # construct authorization header
        headers = dict(Authorization="Basic " + self.b64_user_one_credentials)

        # create test user
        createUserOneRes = self.client.post('api/v0.1/users',
                                            data=json.dumps(self.user_one),
                                            content_type='application/json')

        createUserTwoRes = self.client.post('api/v0.1/users',
                                            data=json.dumps(self.user_two),
                                            content_type='application/json')

        # get user id of first test user, update user dict and put request
        user_id = json.loads(createUserOneRes.get_data(as_text=True))['id']
        self.user_one['email'] = self.user_two['email']

        updateUserOneRes = self.client.put('api/v0.1/users/%s'
                                           % user_id,
                                           data=json.dumps(
                                            self.user_one),
                                           headers=headers,
                                           content_type='application/json')

        self.assertEqual(createUserOneRes.status_code, 201)
        self.assertEqual(createUserTwoRes.status_code, 201)
        self.assertEqual(updateUserOneRes.status_code, 400)
        self.assertIn('email already taken', str(updateUserOneRes.data))

    def test_user_update_fails_when_username_taken(self):
        """Return 400 when updating user email address in use."""
        # construct authorization header
        headers = dict(Authorization="Basic " + self.b64_user_one_credentials)

        # create test user
        createUserOneRes = self.client.post('api/v0.1/users',
                                            data=json.dumps(self.user_one),
                                            content_type='application/json')

        createUserTwoRes = self.client.post('api/v0.1/users',
                                            data=json.dumps(self.user_two),
                                            content_type='application/json')

        # get user id of first test user, update user dict and put request
        user_id = json.loads(createUserOneRes.get_data(as_text=True))['id']
        self.user_one['username'] = self.user_two['username']

        updateUserOneRes = self.client.put('api/v0.1/users/%s'
                                           % user_id,
                                           data=json.dumps(
                                            self.user_one),
                                           headers=headers,
                                           content_type='application/json')

        self.assertEqual(createUserOneRes.status_code, 201)
        self.assertEqual(createUserTwoRes.status_code, 201)
        self.assertEqual(updateUserOneRes.status_code, 400)
        self.assertIn('username already taken', str(updateUserOneRes.data))

    def test_user_update_fails_when_updating_different_user(self):
        """Return 401 when updating another users account."""
        # construct authorization header
        headers = dict(Authorization="Basic " + self.b64_user_one_credentials)

        # create test user
        createUserOneRes = self.client.post('api/v0.1/users',
                                            data=json.dumps(self.user_one),
                                            content_type='application/json')

        createUserTwoRes = self.client.post('api/v0.1/users',
                                            data=json.dumps(self.user_two),
                                            content_type='application/json')

        # get user id of first test user, update user dict and put request
        user_two_id = json.loads(createUserTwoRes.get_data(as_text=True))['id']
        self.user_two['username'] = 'Johnny_updated'
        # updating user two with auth header of user one
        updateUserTwoRes = self.client.put('api/v0.1/users/%s'
                                           % user_two_id,
                                           data=json.dumps(
                                            self.user_two),
                                           headers=headers,
                                           content_type='application/json')

        self.assertEqual(createUserOneRes.status_code, 201)
        self.assertEqual(createUserTwoRes.status_code, 201)
        self.assertEqual(updateUserTwoRes.status_code, 401)
        self.assertIn('you do not have access to this', str(updateUserTwoRes.data))

    def tearDown(self):
        """Teardown all initialized variables."""
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()


if __name__ == "__main__":
    unittest.main()
