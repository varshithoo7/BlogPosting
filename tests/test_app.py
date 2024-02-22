import pytest
from main import app
from flask import session


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def login(client, email, password):
    return client.post('/login', data={'email': email, 'password': password})


def test_get_user_info(client):
    # Simulate logging in
    login(client, 'test@example.com', 'password')

    # Access the /welcome route to retrieve user information
    response = client.get('/welcome')
    assert response.status_code == 302

    # Extract user information from the session
    user_info = {
        'id': session.get('user_id'),
        'first_name': session.get('first_name'),
        'last_name': session.get('last_name'),
        'email': session.get('email')
    }

    # Assert user information matches the expected values
    assert user_info == {
        'id': None,  # Assuming the user is not logged in initially
        'first_name': None,
        'last_name': None,
        'email': None
    }
