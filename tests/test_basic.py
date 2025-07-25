import sys
import os
# Ensure the parent directory is in the Python path so 'app' can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app.main import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    """
    Test the health check endpoint ('/').
    Asserts that the response status is 200 and the returned JSON contains the correct status and service name.
    """

    response = client.get('/')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert data['service'] == 'URL Shortener API'


def test_shorten_and_redirect(client):
    """
    Test shortening a valid URL and redirecting using the short code.
    Asserts that the shortener returns a code and that the redirect works and points to the original URL.
    """

    # Shorten a valid URL
    resp = client.post('/api/shorten', json={"url": "https://www.google.com"})
    assert resp.status_code == 200

    data = resp.get_json()
    assert 'short_code' in data
    code = data['short_code']

    # Redirect
    resp2 = client.get(f'/{code}', follow_redirects=False)

    assert resp2.status_code == 302
    assert resp2.headers['Location'] == 'https://www.google.com'

def test_invalid_url(client):
    """
    Test submitting an invalid URL to the shortener.
    Asserts that the response status is 400 and an error message is returned.
    """

    resp = client.post('/api/shorten', json={"url": "not_a_url"})
    assert resp.status_code == 400
    assert 'error' in resp.get_json()

def test_missing_url(client):
    """
    Test submitting a request with a missing 'url' key to the shortener.
    Asserts that the response status is 400 and an error message is returned.
    """
    
    resp = client.post('/api/shorten', json={})
    assert resp.status_code == 400
    assert 'error' in resp.get_json()