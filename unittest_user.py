import unittest
import os
import json
from app import create_app, db


class UserTestCase(unittest.TestCase):
    """Class representing user unit tests."""

    def setUp(self):
        """Initialize app and set up test variables."""
        self.app = create_app(config_mode='testing')
        self.client = self.app.test_client
        self.user = {'name': 'Hans',
                     'lastname': 'Gruber',
                     'username': 'hansi',
                     'email': 'hans.gruber@nakatomi.com',
                     'password': 'python'}

        with self.app.app_context():
            db.create_all()

    def test_user_creation(self):
        """Test API can create a new user (POST request)"""
        res = self.client().post('api/v0.1/users', data=self.user)
        self.assertEqual(res.status_code, 201)


if __name__ == "__main__":
    unittest.main()
