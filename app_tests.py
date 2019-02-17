import unittest
from peewee import *
import app
from functools import wraps
import forms
from models import User, Post, Relationship

TEST_DB = SqliteDatabase(':memory:')
TEST_DB.connect()
TEST_DB.create_tables([User, Post, Relationship], safe=True)
MODELS = (User, Post, Relationship)
USER_DATA = {
    'email': 'test_0@example.com',
    'password': 'password'
}

def use_test_database(fn):
    @wraps(fn)
    def inner(self):
        with TEST_DB.bind_ctx(MODELS):
            TEST_DB.create_tables(MODELS)
            try:
                fn(self)
            finally:
                TEST_DB.drop_tables(MODELS)
    return inner

class UserModelTestCase(unittest.TestCase):
    @staticmethod
    def create_users(count=2):
        for i in range(count):
            User.create_user(
                email='test_{}@example.com'.format(i),
                password='password'
            )

    def test_create_user(self):
        with use_test_database(self):
            self.create_users()
            self.assertEqual(User.select().count(), 2)
            self.assertNotEqual(
                User.select().get().password,
                'password'
            )

    def test_create_duplicate_user(self):
        with use_test_database(self):
            self.create_users()
            with self.assertRaises(ValueError):
                User.create_user(
                    email='test_1@example.com',
                    password='password'
                )

class ViewTestCase(unittest.TestCase):
    def setUp(self):
        app.app.config['TESTING'] = True
        app.app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.app.test_client()

class UserViewsTestCase(ViewTestCase):
    def test_registration(self):
        data = {
            'email': 'test@example.com',
            'password': 'password',
            'password2': 'password'
        }
        with use_test_database(self):
            rv = self.app.post(
                '/register',
                data=data)
            self.assertEqual(rv.status_code, 302)
            self.assertEqual(rv.location, 'http://localhost/')

if __name__ == '__main__':
    unittest.main()