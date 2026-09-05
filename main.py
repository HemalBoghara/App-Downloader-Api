"""
Multi-Platform Video Downloader REST API
Supports: Instagram, Facebook, YouTube
Built with FastAPI and yt-dlp
"""

import os
from pathlib import Path
from typing import Optional
import requests
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from downloader import (
    extract_instagram_info,
    extract_facebook_info,
    extract_youtube_info,
    extract_media_info,
    is_valid_instagram_url,
    is_valid_facebook_url,
    is_valid_youtube_url,
    detect_platform,
)

app = FastAPI(
    title="Multi-Platform Video Downloader API",
    description="High-performance REST API to extract media metadata and download videos from Instagram, Facebook, and YouTube.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory
STATIC_DIR = Path(__file__).resolve().parent / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# Pydantic Schemas
class MediaRequest(BaseModel):
    url: str = Field(
        ...,
        description="The video URL from Instagram, Facebook, or YouTube",
        examples=["https://www.instagram.com/reel/..."]
    )


class MediaResponse(BaseModel):
    success: bool
    platform: Optional[str] = None
    id: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    uploader: Optional[str] = None
    uploader_id: Optional[str] = None
    thumbnail: Optional[str] = None
    duration: Optional[float] = None
    view_count: Optional[int] = None
    like_count: Optional[int] = None
    comment_count: Optional[int] = None
    video_url: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    ext: Optional[str] = "mp4"
    source_url: str


def execute_extraction(url: str, expected_platform: Optional[str] = None) -> dict:
    """Helper to validate, extract and format media response."""
    if not url or not url.strip():
        raise HTTPException(status_code=400, detail="URL parameter cannot be empty.")

    url = url.strip()
    detected = detect_platform(url)

    if expected_platform and detected != expected_platform.lower():
        raise HTTPException(
            status_code=400,
            detail=f"Expected a {expected_platform.capitalize()} URL, but received a {detected.capitalize()} or unsupported link."
        )

    if detected == "unknown":
        raise HTTPException(
            status_code=400,
            detail="Unsupported URL. Supported platforms: Instagram, Facebook, YouTube."
        )

    try:
        data = extract_media_info(url, platform_hint=expected_platform)
        return data
    except PermissionError as pe:
        raise HTTPException(status_code=403, detail=str(pe))
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")


def stream_media_response(info: dict):
    """Helper to stream remote video directly as downloadable MP4 attachment."""
    video_direct_url = info.get("video_url")
    platform = info.get("platform") or "video"
    video_id = info.get("id") or "download"
    filename = f"{platform}_{video_id}.mp4"

    try:
        headers = {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/124.0.0.0 Safari/537.36'
            )
        }
        req = requests.get(video_direct_url, stream=True, headers=headers, timeout=40)
        req.raise_for_status()

        def iterfile():
            for chunk in req.iter_content(chunk_size=128 * 1024):
                if chunk:
                    yield chunk

        content_type = req.headers.get("content-type", "video/mp4")
        content_length = req.headers.get("content-length")

        response_headers = {
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Access-Control-Expose-Headers": "Content-Disposition",
        }
        if content_length:
            response_headers["Content-Length"] = content_length

        return StreamingResponse(
            iterfile(),
            media_type=content_type,
            headers=response_headers
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stream video download: {str(e)}")


# -------------------------------------------------------------
# General Endpoints
# -------------------------------------------------------------
@app.get("/", response_class=HTMLResponse, tags=["General"])
async def root():
    """Serves the Web Tester UI."""
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return HTMLResponse("<h1>Multi-Platform Video Downloader API</h1><p>Visit <a href='/docs'>/docs</a> for interactive API documentation.</p>")


@app.get("/health", tags=["General"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "Multi-Platform Video Downloader API", "version": "2.0.0"}


# -------------------------------------------------------------
# 1. Instagram Dedicated Endpoints
# -------------------------------------------------------------
@app.get("/api/instagram/info", response_model=MediaResponse, tags=["Instagram API"])
async def instagram_info_get(
    url: str = Query(..., description="Instagram Reel or Post URL", examples=["https://www.instagram.com/reel/..."])
):
    """Extract Instagram Reel or Post video metadata and direct MP4 URL (GET)."""
    return execute_extraction(url, "instagram")


@app.post("/api/instagram/info", response_model=MediaResponse, tags=["Instagram API"])
async def instagram_info_post(payload: MediaRequest):
    """Extract Instagram Reel or Post video metadata and direct MP4 URL (POST)."""
    return execute_extraction(payload.url, "instagram")


@app.get("/api/instagram/download", tags=["Instagram API"])
async def instagram_download(
    url: str = Query(..., description="Instagram Reel or Post URL to download directly")
):
    """Directly stream and download Instagram video file (.mp4)."""
    info = execute_extraction(url, "instagram")
    return stream_media_response(info)


# -------------------------------------------------------------
# 2. Facebook Dedicated Endpoints
# -------------------------------------------------------------
@app.get("/api/facebook/info", response_model=MediaResponse, tags=["Facebook API"])
async def facebook_info_get(
    url: str = Query(..., description="Facebook Reel or Video URL", examples=["https://www.facebook.com/reel/..."])
):
    """Extract Facebook Video / Reel metadata and direct MP4 URL (GET)."""
    return execute_extraction(url, "facebook")


@app.post("/api/facebook/info", response_model=MediaResponse, tags=["Facebook API"])
async def facebook_info_post(payload: MediaRequest):
    """Extract Facebook Video / Reel metadata and direct MP4 URL (POST)."""
    return execute_extraction(payload.url, "facebook")


@app.get("/api/facebook/download", tags=["Facebook API"])
async def facebook_download(
    url: str = Query(..., description="Facebook Reel or Video URL to download directly")
):
    """Directly stream and download Facebook video file (.mp4)."""
    info = execute_extraction(url, "facebook")
    return stream_media_response(info)


# -------------------------------------------------------------
# 3. YouTube Dedicated Endpoints
# -------------------------------------------------------------
@app.get("/api/youtube/info", response_model=MediaResponse, tags=["YouTube API"])
async def youtube_info_get(
    url: str = Query(..., description="YouTube Video or Shorts URL", examples=["https://www.youtube.com/shorts/..."])
):
    """Extract YouTube Video or Shorts metadata and direct MP4 URL (GET)."""
    return execute_extraction(url, "youtube")


@app.post("/api/youtube/info", response_model=MediaResponse, tags=["YouTube API"])
async def youtube_info_post(payload: MediaRequest):
    """Extract YouTube Video or Shorts metadata and direct MP4 URL (POST)."""
    return execute_extraction(payload.url, "youtube")


@app.get("/api/youtube/download", tags=["YouTube API"])
async def youtube_download(
    url: str = Query(..., description="YouTube Video or Shorts URL to download directly")
):
    """Directly stream and download YouTube video file (.mp4)."""
    info = execute_extraction(url, "youtube")
    return stream_media_response(info)


# -------------------------------------------------------------
# 4. Universal Smart Endpoints (Auto-detects platform)
# -------------------------------------------------------------
@app.get("/api/universal/info", response_model=MediaResponse, tags=["Universal API"])
@app.get("/api/info", response_model=MediaResponse, tags=["Universal API"])
async def universal_info_get(
    url: str = Query(..., description="Instagram, Facebook, or YouTube URL")
):
    """Auto-detects platform and extracts metadata with direct MP4 URL (GET)."""
    return execute_extraction(url)


@app.post("/api/universal/info", response_model=MediaResponse, tags=["Universal API"])
@app.post("/api/info", response_model=MediaResponse, tags=["Universal API"])
async def universal_info_post(payload: MediaRequest):
    """Auto-detects platform and extracts metadata with direct MP4 URL (POST)."""
    return execute_extraction(payload.url)


@app.get("/api/universal/download", tags=["Universal API"])
@app.get("/api/download", tags=["Universal API"])
async def universal_download(
    url: str = Query(..., description="Instagram, Facebook, or YouTube URL to download")
):
    """Auto-detects platform and streams direct downloadable MP4 file."""
    info = execute_extraction(url)
    return stream_media_response(info)


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print(f"Starting Multi-Platform Video Downloader API on http://0.0.0.0:{port} ...")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
