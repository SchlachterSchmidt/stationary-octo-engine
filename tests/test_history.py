"""Basic Histroy endpoint unit test."""

import unittest
import json
from app import create_app
from app.models import db


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

    def test_create_new_history_record():
        """Returns 200 and 'record created' message."""
        # TODO: everything
        pass

    def test_add_to_existing_history_record():
        """Returns 200 and 'record updated' message."""
        # TODO: everything
        pass

    def test_get_existing_history_record():
        """Returns 200 and history object as JSON"""
        # TODO: everything
        pass

    def test_get_non_existing_history_record():
        """Returns 404 and 'record not found' message"""
        # TODO: everything
        pass

    def tearDown(self):
        """Teardown all initialized variables."""
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()


if __name__ == "__main__":
    unittest.main()
