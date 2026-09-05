"""
Multi-Platform Media Extractor and Downloader
Supports: Instagram, Facebook, YouTube
Powered by yt-dlp
"""

import re
from typing import Dict, Any, Optional
import yt_dlp


def detect_platform(url: str) -> str:
    """Detect the social media platform from a given URL."""
    url = url.strip().lower()
    if any(k in url for k in ["instagram.com", "instagr.am"]):
        return "instagram"
    elif any(k in url for k in ["facebook.com", "fb.watch", "fb.com", "fb.gg"]):
        return "facebook"
    elif any(k in url for k in ["youtube.com", "youtu.be"]):
        return "youtube"
    return "unknown"


def is_valid_platform_url(url: str, expected_platform: Optional[str] = None) -> bool:
    """Validate if URL belongs to expected platform or any supported platform."""
    detected = detect_platform(url)
    if expected_platform:
        return detected == expected_platform.lower()
    return detected in ["instagram", "facebook", "youtube"]


def is_valid_instagram_url(url: str) -> bool:
    return is_valid_platform_url(url, "instagram")


def is_valid_facebook_url(url: str) -> bool:
    return is_valid_platform_url(url, "facebook")


def is_valid_youtube_url(url: str) -> bool:
    return is_valid_platform_url(url, "youtube")


def extract_media_info(url: str, platform_hint: Optional[str] = None) -> Dict[str, Any]:
    """
    Extract comprehensive metadata and direct download stream URL for Instagram, Facebook, or YouTube.
    """
    url = url.strip()
    detected_platform = platform_hint or detect_platform(url)

    # yt-dlp configuration
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'format': 'best[ext=mp4]/best',
        'http_headers': {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/124.0.0.0 Safari/537.36'
            ),
            'Accept-Language': 'en-US,en;q=0.9',
        },
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info:
                raise ValueError(f"Could not extract any media information from this {detected_platform.capitalize()} URL.")

            # If playlist/multi-entry, pick the first entry
            if 'entries' in info and info['entries']:
                info = info['entries'][0]

            # Find best direct video URL
            video_url = info.get('url')
            if not video_url and 'formats' in info and len(info['formats']) > 0:
                best_format = None
                for f in reversed(info['formats']):
                    if f.get('url') and (f.get('vcodec') != 'none' or f.get('ext') == 'mp4'):
                        best_format = f
                        break
                if not best_format:
                    best_format = info['formats'][-1]
                video_url = best_format.get('url')

            title = info.get("title") or info.get("description") or f"{detected_platform.capitalize()} Video"
            # Clean title
            if len(title) > 120:
                title = title[:117] + "..."

            result = {
                "success": True,
                "platform": detected_platform,
                "id": str(info.get("id", "")),
                "title": title,
                "description": info.get("description") or "",
                "uploader": info.get("uploader") or info.get("channel") or info.get("uploader_id") or "Unknown",
                "uploader_id": info.get("uploader_id"),
                "thumbnail": info.get("thumbnail"),
                "duration": info.get("duration"),  # seconds
                "view_count": info.get("view_count"),
                "like_count": info.get("like_count"),
                "comment_count": info.get("comment_count"),
                "video_url": video_url,
                "width": info.get("width"),
                "height": info.get("height"),
                "ext": info.get("ext") or "mp4",
                "source_url": url,
            }

            if not result["video_url"]:
                raise ValueError("Direct video stream URL could not be extracted. The content might be private, age-restricted, or audio-only.")

            return result

    except yt_dlp.utils.DownloadError as e:
        err = str(e)
        if "Private" in err or "login" in err.lower():
            raise PermissionError(f"This {detected_platform.capitalize()} post is private or requires authentication.")
        if "Sign in to confirm you’re not a bot" in err:
            raise PermissionError("Platform is requiring verification. Try another video link.")
        raise RuntimeError(f"Download extraction error: {err}")
    except Exception as e:
        raise RuntimeError(f"Extraction failed: {str(e)}")


# Dedicated platform extraction wrappers
def extract_instagram_info(url: str) -> Dict[str, Any]:
    return extract_media_info(url, "instagram")


def extract_facebook_info(url: str) -> Dict[str, Any]:
    return extract_media_info(url, "facebook")


def extract_youtube_info(url: str) -> Dict[str, Any]:
    return extract_media_info(url, "youtube")
