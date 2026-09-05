"""
Automated unit and integration tests for Multi-Platform Video Downloader API
"""

import sys
from fastapi.testclient import TestClient
from main import app
from downloader import (
    detect_platform,
    is_valid_instagram_url,
    is_valid_facebook_url,
    is_valid_youtube_url,
)

client = TestClient(app)


def test_platform_detection():
    assert detect_platform("https://www.instagram.com/reel/C8abc123/") == "instagram"
    assert detect_platform("https://instagram.com/p/C9xyz456/") == "instagram"
    assert detect_platform("https://www.facebook.com/reel/123456789") == "facebook"
    assert detect_platform("https://fb.watch/abcd123/") == "facebook"
    assert detect_platform("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == "youtube"
    assert detect_platform("https://youtu.be/dQw4w9WgXcQ") == "youtube"
    assert detect_platform("https://youtube.com/shorts/abcdef123") == "youtube"
    assert detect_platform("https://example.com/other") == "unknown"


def test_url_validators():
    assert is_valid_instagram_url("https://www.instagram.com/reel/C8abc/") == True
    assert is_valid_instagram_url("https://www.facebook.com/reel/123") == False

    assert is_valid_facebook_url("https://www.facebook.com/watch/?v=123") == True
    assert is_valid_facebook_url("https://youtube.com/watch?v=123") == False

    assert is_valid_youtube_url("https://youtu.be/123") == True
    assert is_valid_youtube_url("https://instagram.com/p/123") == False


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["version"] == "2.0.0"


def test_root_html_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "Multi-Platform Video Downloader" in response.text


def test_platform_mismatch_rejection():
    # Sending a YouTube URL to Instagram endpoint should fail with 400
    response = client.get("/api/instagram/info?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    assert response.status_code == 400
    assert "Expected a Instagram URL" in response.json()["detail"]

    # Sending an Instagram URL to Facebook endpoint should fail with 400
    response = client.get("/api/facebook/info?url=https://www.instagram.com/reel/C8abc/")
    assert response.status_code == 400
    assert "Expected a Facebook URL" in response.json()["detail"]


def test_empty_and_unknown_urls():
    response = client.get("/api/universal/info?url=")
    assert response.status_code == 400

    response = client.get("/api/universal/info?url=https://wikipedia.org")
    assert response.status_code == 400
    assert "Unsupported URL" in response.json()["detail"]


if __name__ == "__main__":
    print("Running automated multi-platform tests...")
    test_platform_detection()
    print("[PASSED] Platform Detection Tests")
    test_url_validators()
    print("[PASSED] Platform URL Validator Tests")
    test_health_endpoint()
    print("[PASSED] Health Endpoint Tests")
    test_root_html_endpoint()
    print("[PASSED] Web UI Root Tests")
    test_platform_mismatch_rejection()
    print("[PASSED] Cross-Platform Mismatch Rejection Tests")
    test_empty_and_unknown_urls()
    print("[PASSED] Empty & Unsupported URL Tests")
    print("\nALL MULTI-PLATFORM TESTS PASSED SUCCESSFULLY!")
