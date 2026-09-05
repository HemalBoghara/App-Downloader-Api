"""
GitHub Auto-Uploader Script
Creates repository and pushes all project files directly using GitHub REST API.
"""

import os
import sys
import base64
import requests
from pathlib import Path

REPO_NAME = "App-Downloader-Api"
REPO_DESCRIPTION = "Instagram Video and Reel Downloader REST API (FastAPI & yt-dlp)"
PROJECT_DIR = Path(__file__).resolve().parent


def get_all_files():
    """List all files in the project, respecting .gitignore rules."""
    files_to_upload = []
    ignored_patterns = {
        "__pycache__", ".git", ".env", ".venv", "venv", "env", ".pytest_cache", ".DS_Store"
    }
    
    for path in PROJECT_DIR.rglob("*"):
        if path.is_file():
            parts = path.relative_to(PROJECT_DIR).parts
            if any(ignored in parts for ignored in ignored_patterns):
                continue
            if path.name.endswith(('.pyc', '.pyo', '.tmp')):
                continue
            files_to_upload.append(path)
    return files_to_upload


def upload_to_github(token: str):
    token = token.strip()
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "App-Downloader-Api-Uploader"
    }

    # 1. Verify Token & Get Authenticated User
    print("Connecting to GitHub...")
    user_resp = requests.get("https://api.github.com/user", headers=headers)
    if user_resp.status_code != 200:
        print(f"[ERROR] GitHub authentication failed (Status {user_resp.status_code}):")
        print(user_resp.text)
        return False

    username = user_resp.json()["login"]
    print(f"[OK] Logged in as: {username}")

    # 2. Check Repository
    repo_url = f"https://api.github.com/repos/{username}/{REPO_NAME}"
    check_repo = requests.get(repo_url, headers=headers)
    if check_repo.status_code != 200:
        print(f"[ERROR] Could not access repository {username}/{REPO_NAME}: {check_repo.status_code}")
        print(check_repo.text)
        return False

    print(f"[OK] Repository found: https://github.com/{username}/{REPO_NAME}")

    # 3. Upload Each File
    files = get_all_files()
    print(f"\nUploading {len(files)} files to repository...")

    success_count = 0
    for file_path in files:
        rel_path = file_path.relative_to(PROJECT_DIR).as_posix()
        try:
            with open(file_path, "rb") as f:
                content_bytes = f.read()
            content_b64 = base64.b64encode(content_bytes).decode("utf-8")

            file_api_url = f"https://api.github.com/repos/{username}/{REPO_NAME}/contents/{rel_path}"
            file_check = requests.get(file_api_url, headers=headers)
            
            payload = {
                "message": f"Add {rel_path}",
                "content": content_b64,
            }
            if file_check.status_code == 200:
                payload["sha"] = file_check.json()["sha"]
                payload["message"] = f"Update {rel_path}"

            put_resp = requests.put(file_api_url, headers=headers, json=payload)
            if put_resp.status_code in (200, 201):
                print(f"  [OK] Uploaded: {rel_path}")
                success_count += 1
            else:
                resp_json = put_resp.json()
                print(f"  [FAIL] {rel_path} (Status {put_resp.status_code}): {resp_json.get('message', put_resp.text)}")
        except Exception as e:
            print(f"  [ERROR] on {rel_path}: {e}")

    print("\n" + "="*60)
    if success_count == len(files):
        print("All files successfully pushed to GitHub!")
    else:
        print(f"Uploaded {success_count}/{len(files)} files.")
    print(f"Repository URL: https://github.com/{username}/{REPO_NAME}")
    print("="*60)
    return success_count > 0


if __name__ == "__main__":
    token = os.getenv("GITHUB_TOKEN")
    if not token and len(sys.argv) > 1:
        token = sys.argv[1]

    if not token:
        token = input("Enter your GitHub Token: ").strip()

    if token:
        upload_to_github(token)
    else:
        print("[ERROR] Token was not provided.")
