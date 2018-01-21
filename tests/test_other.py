"""Basic User endpoint unit test."""

import unittest
from app import create_app
from app.models import db


class OtherTestCase(unittest.TestCase):
    """Class representing various other unit tests."""

    def setUp(self):
        """Initialize app and set up test variables."""
        self.app = create_app(config_mode='testing')
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

    def test_check_health(self):
        """200 and hello world message"""
        res = self.client.get('/api/v0.1/health')

        self.assertEqual(res.status_code, 200)
        self.assertIn('"hello": "world"', str(res.data))

    def tearDown(self):
        """Teardown all initialized variables."""
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()


if __name__ == "__main__":
    unittest.main()
