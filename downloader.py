"""
Instagram Media Extractor and Downloader using yt-dlp
"""

import re
from typing import Dict, Any, Optional
import yt_dlp


def is_valid_instagram_url(url: str) -> bool:
    """Validate if the provided URL is a valid Instagram media link."""
    patterns = [
        r"https?:\/\/(www\.)?instagram\.com\/p\/[a-zA-Z0-9_\-\.\/]+",
        r"https?:\/\/(www\.)?instagram\.com\/reel\/[a-zA-Z0-9_\-\.\/]+",
        r"https?:\/\/(www\.)?instagram\.com\/reels\/[a-zA-Z0-9_\-\.\/]+",
        r"https?:\/\/(www\.)?instagram\.com\/tv\/[a-zA-Z0-9_\-\.\/]+",
        r"https?:\/\/(www\.)?instagram\.com\/share\/reel\/[a-zA-Z0-9_\-\.\/]+",
        r"https?:\/\/(www\.)?instagram\.com\/share\/p\/[a-zA-Z0-9_\-\.\/]+",
    ]
    return any(re.match(pattern, url.strip()) for pattern in patterns) or ("instagram.com" in url)


def extract_instagram_info(url: str) -> Dict[str, Any]:
    """
    Extract comprehensive information and download links from an Instagram post/reel.
    """
    url = url.strip()

    # yt-dlp configuration options
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'format': 'best',
        'http_headers': {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/122.0.0.0 Safari/537.36'
            ),
            'Accept-Language': 'en-US,en;q=0.9',
        },
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info:
                raise ValueError("Could not extract any media information from this URL.")

            # If it's a playlist or multiple items, pick the first or primary
            if 'entries' in info and info['entries']:
                info = info['entries'][0]

            # Extract best video URL
            video_url = None
            if 'url' in info:
                video_url = info['url']
            elif 'formats' in info and len(info['formats']) > 0:
                # Filter for formats that have both video or highest resolution
                best_format = None
                for f in reversed(info['formats']):
                    if f.get('url') and (f.get('vcodec') != 'none' or f.get('ext') == 'mp4'):
                        best_format = f
                        break
                if not best_format:
                    best_format = info['formats'][-1]
                video_url = best_format.get('url')

            # Build clean response payload
            result = {
                "success": True,
                "id": info.get("id"),
                "title": info.get("title") or info.get("description") or "Instagram Video",
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
                raise ValueError("Direct video stream URL could not be found. The content might be private or an image.")

            return result

    except yt_dlp.utils.DownloadError as e:
        error_msg = str(e)
        if "Private" in error_msg or "login" in error_msg.lower():
            raise PermissionError("This post is private or requires login to view.")
        raise RuntimeError(f"Download error: {error_msg}")
    except Exception as e:
        raise RuntimeError(f"Extraction failed: {str(e)}")
