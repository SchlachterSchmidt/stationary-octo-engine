"""Testrunner discovering and running all tests in /tests dir."""

import unittest
from flask_script import Manager

from app import create_app

app = create_app(config_mode='testing')
manager = Manager(app)


@manager.command
def classifier():
    """Run the classifier unit tests in /tests dir."""
    tests = unittest.TestLoader().discover('./tests',
                                           pattern='test_classifier*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1


@manager.command
def user():
    """Run the user unit tests in /tests dir."""
    tests = unittest.TestLoader().discover('./tests', pattern='test_user*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1


@manager.command
def all():
    """Run all unit tests in /tests dir."""
    tests = unittest.TestLoader().discover('./tests', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1


if __name__ == '__main__':
    manager.run()
