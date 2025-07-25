import sys
import os

# Ensure the parent directory is in the Python path so 'app' can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import concurrent.futures
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

def test_404_on_unknown_short_code(client):
    """
    Test accessing a non-existent short code.
    Asserts that the response status is 404.
    """

    resp = client.get('/not_real_shortcode')
    assert resp.status_code == 404

def test_stats(client):
    """
    Test the stats endpoint for a valid short code.
    Shortens a URL, accesses it twice, and checks that the click count and original URL are correct in the stats response.
    """

    # Shorten and use
    resp = client.post('/api/shorten', json={"url": "https://pytest.org"})
    code = resp.get_json()['short_code']

    # Click twice
    client.get(f'/{code}')
    client.get(f'/{code}')

    # Get the stats for 'code' 
    stats = client.get(f'/api/stats/{code}')
    data = stats.get_json()

    # Assert that the stats are correct
    assert data['url'] == 'https://pytest.org'
    assert data['clicks'] == 2
    assert 'created_at' in data

def test_stats_404(client):
    """
    Test the stats endpoint for a non-existent short code.
    Asserts that the response status is 404 and an error message is returned.
    """

    resp = client.get('/api/stats/short_code_does_not_exist')
    assert resp.status_code == 404
    assert 'error' in resp.get_json()

def test_thread_safety():
    """
    Test thread safety by sending multiple concurrent shorten requests.
    Ensures all short codes are unique and all URLs are stored.
    """
    urls = [f"https://example.com/{i}" for i in range(20)]
    results = []

    def shorten(url):
        with app.test_client() as client:
            resp = client.post('/api/shorten', json={"url": url})
            assert resp.status_code == 200
            return resp.get_json()['short_code']

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor: # Creates a pool of 10 worker threads
        futures = [executor.submit(shorten, url) for url in urls]   # Submit shorten function to the thread pool to be executed
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())

    # Check all short codes are unique
    assert len(set(results)) == len(urls)