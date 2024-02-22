import pytest
from main import app


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_signup(client):
    # Test signup functionality
    response = client.post('/signup', data={
        'first_name': 'Test1', 'last_name': 'User',
        'email': 'test123@example.com',
        'password': 'password', 'confirm_password': 'password'})
    assert response.status_code == 200  # Check for successful signup redirect


def test_logout(client):
    # Access a route that requires authentication to login
    client.post('/login', data={
        'email': 'test123@example.com', 'password': 'password'},
                follow_redirects=True)

    # Perform logout
    response = client.get('/logout', follow_redirects=True)

    # Check if the user is redirected to the home page
    assert response.status_code == 200
