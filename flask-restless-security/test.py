import os
from application import app
from server import user_datastore
from database import db
import unittest
import tempfile
import re
import json

from flask_security.utils import encrypt_password
from flask_security import current_user
from flask_security.utils import login_user
from models import User, Role, SomeStuff


class FlaskTestCase(unittest.TestCase):
    def setUp(self):
        app.config.from_object('config.TestingConfig')
        self.client = app.test_client()

        db.init_app(app)
        with app.app_context():
            db.create_all()
            user_datastore.create_user(email='test', password=encrypt_password('test'))
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def _post(self, route, data=None, content_type=None, follow_redirects=True, headers=None):
        content_type = content_type or 'application/x-www-form-urlencoded'
        return self.client.post(route, data=data, follow_redirects=follow_redirects, content_type=content_type,
                                headers=headers)

    def _login(self, email=None, password=None):
        # Get CSRF token from login form
        csrf_token = ''
        rv = self.client.get('/login')
        matches = re.findall('name="csrf_token".*?value="(.*?)"', rv.data.decode())
        if matches:
            csrf_token = matches[0]

        # POST login form
        email = email or 'test'
        password = password or 'test'
        data = {
            'email': email,
            'password': password,
            'remember': 'y',
            'csrf_token': csrf_token
        }
        return self._post('/login', data=data, follow_redirects=False)


class ModelsTest(FlaskTestCase):
    def test_protectedstuff(self):
        with app.app_context():
            instance = SomeStuff(data1=1337, data2='Test')
            db.session.add(instance)
            db.session.commit()
            self.assertTrue(hasattr(instance, 'id'))


class ViewsTest(FlaskTestCase):
    def test_page(self):
        rv = self.client.get('/')
        self.assertEqual(200, rv.status_code)

    def test_protected_page(self):
        rv = self.client.get('/mypage')
        self.assertIn('Redirecting...', rv.data.decode())

        self._login()

        rv = self.client.get('/mypage')
        self.assertIn('It works', rv.data.decode())

        rv = self.client.get('/logout')
        self.assertEqual(302, rv.status_code)


class APITest(FlaskTestCase):
    def _auth(self, username=None, password=None):
        username = username or 'test'
        password = password or 'test'
        rv = self._post('/api/v1/auth',
                        data=json.dumps({'username': username, 'password': password})
                        )
        return json.loads(rv.data.decode())

    def _get(self, route, data=None, content_type=None, follow_redirects=True, headers=None):
        content_type = content_type or 'application/json'
        if hasattr(self, 'token'):
            headers = headers or {'Authorization': 'JWT ' + self.token}
        return self.client.get(route, data=data, follow_redirects=follow_redirects, content_type=content_type,
                               headers=headers)

    def _post(self, route, data=None, content_type=None, follow_redirects=True, headers=None):
        content_type = content_type or 'application/json'
        if hasattr(self, 'token'):
            headers = headers or {'Authorization': 'Bearer ' + self.token}
        return self.client.post(route, data=data, follow_redirects=follow_redirects, content_type=content_type,
                                headers=headers)

    def test_auth(self):
        # Get auth token with invalid credentials
        auth_resp = self._auth('not', 'existing')
        self.assertEqual(401, auth_resp['status_code'])

        # Get auth token with valid credentials
        auth_resp = self._auth('test', 'test')
        self.assertIn(u'access_token', auth_resp)

        self.token = auth_resp['access_token']

        # Get empty collection
        rv = self._get('/api/v1/protected_stuff')
        self.assertEqual(200, rv.status_code)
        data = json.loads(rv.data.decode())
        self.assertEqual(data['num_results'], 0)

        # Post object to collection
        rv = self._post('/api/v1/protected_stuff', data=json.dumps({'data1': 1337, 'data2': 'Test'}))
        self.assertEqual(201, rv.status_code)

        # Get collection if new object
        rv = self._get('/api/v1/protected_stuff')
        data = json.loads(rv.data.decode())
        self.assertEqual(data['num_results'], 1)

        # Post another object and get it back
        rv = self._post('/api/v1/protected_stuff', data=json.dumps({'data1': 2, 'data2': ''}))
        self.assertEqual(201, rv.status_code)
        rv = self._get('/api/v1/protected_stuff/2')
        data = json.loads(rv.data.decode())
        self.assertEqual(data['data1'], 2)


if __name__ == '__main__':
    unittest.main()
