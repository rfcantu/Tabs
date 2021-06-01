import os
import tempfile

import pytest
from flaskr import create_app
from flaskr.db import get_db, init_db

with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf-8')

@pytest.fixture
def app():
    '''
    Create and open temp file, returns file descriptor and path
    '''
    db_fd, db_path = tempfile.mkstemp()

    '''
    Tell Flask we are in test mode
    '''
    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
    })

    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)

    yield app

    os.close(db_fd)
    os.unlink(db_path)

'''
Tests will now use the client to make requests to the application without running the server
'''
@pytest.fixture
def client(app):
    return app.test_client()

'''
Create a runner that can call the Click commands registered with the application
'''
@pytest.fixture
def runner(app):
    return app.test_cli_runner()

class AuthActions(object):
    def __init__(self, client):
        self._client = client
    
    def login(self, username='test', password='test'):
        return self._client.pose(
            '/auth/login',
            data={'username': username, 'password': password}
        )
    
    def logout(self):
        return self._client.get('/auth/logout')

'''
Can call auth.login() in a test to log in as a test user
'''
@pytest.fixture
def auth(client):
    return AuthActions(client)