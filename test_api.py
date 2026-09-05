"""
Automated unit and integration tests for Instagram Video Downloader API
"""

import sys
from fastapi.testclient import TestClient
from main import app
from downloader import is_valid_instagram_url

client = TestClient(app)


def test_valid_urls():
    assert is_valid_instagram_url("https://www.instagram.com/reel/C8abc123/") == True
    assert is_valid_instagram_url("https://instagram.com/p/C9xyz456/") == True
    assert is_valid_instagram_url("https://www.instagram.com/tv/C012345/") == True
    assert is_valid_instagram_url("https://google.com") == False


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "Instagram Video Downloader API"}


def test_root_html_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "Instagram Video Downloader" in response.text


def test_invalid_url_info():
    response = client.get("/api/info?url=https://invalid-url.com/something")
    assert response.status_code == 400
    assert "Invalid Instagram URL" in response.json()["detail"]


def test_empty_url():
    response = client.get("/api/info?url=")
    assert response.status_code == 400


if __name__ == "__main__":
    print("Running automated tests...")
    test_valid_urls()
    print("[PASSED] URL Validator Tests")
    test_health_endpoint()
    print("[PASSED] Health Endpoint Tests")
    test_root_html_endpoint()
    print("[PASSED] Web UI Root Endpoint Tests")
    test_invalid_url_info()
    print("[PASSED] Invalid URL rejection Tests")
    test_empty_url()
    print("[PASSED] Empty URL rejection Tests")
    print("\nALL TESTS PASSED SUCCESSFULLY!")
