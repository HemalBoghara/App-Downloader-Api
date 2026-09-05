"""
Instagram Video Downloader REST API
Built with FastAPI and yt-dlp
"""

import os
from pathlib import Path
from typing import Optional
import requests
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from downloader import extract_instagram_info, is_valid_instagram_url

app = FastAPI(
    title="Instagram Video Downloader API",
    description="High-performance API to extract metadata and download Instagram Reels, Videos, and Posts.",
    version="1.0.0",
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


class InstagramRequest(BaseModel):
    url: str = Field(
        ...,
        description="The Instagram Post or Reel URL",
        examples=["https://www.instagram.com/reel/C8.../"]
    )


class InstagramResponse(BaseModel):
    success: bool
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


@app.get("/", response_class=HTMLResponse, tags=["General"])
async def root():
    """Serves the Web Tester UI interface."""
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return HTMLResponse("<h1>Instagram Video Downloader API</h1><p>Visit <a href='/docs'>/docs</a> for API documentation.</p>")


@app.get("/health", tags=["General"])
async def health_check():
    """Health check endpoint to verify server status."""
    return {"status": "healthy", "service": "Instagram Video Downloader API"}


@app.post("/api/info", response_model=InstagramResponse, tags=["Instagram API"])
async def get_video_info_post(payload: InstagramRequest):
    """
    Extract video information and direct download URL using JSON POST request.
    """
    return process_info_request(payload.url)


@app.get("/api/info", response_model=InstagramResponse, tags=["Instagram API"])
async def get_video_info_get(
    url: str = Query(..., description="Instagram Reel or Post URL", examples=["https://www.instagram.com/reel/..."])
):
    """
    Extract video information and direct download URL using GET query parameter.
    """
    return process_info_request(url)


def process_info_request(url: str) -> dict:
    if not url or not url.strip():
        raise HTTPException(status_code=400, detail="URL parameter cannot be empty.")

    url = url.strip()
    if not is_valid_instagram_url(url):
        raise HTTPException(status_code=400, detail="Invalid Instagram URL format.")

    try:
        data = extract_instagram_info(url)
        return data
    except PermissionError as pe:
        raise HTTPException(status_code=403, detail=str(pe))
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch video: {str(e)}")


@app.get("/api/download", tags=["Instagram API"])
async def download_video(
    url: str = Query(..., description="Instagram Reel or Post URL to download directly")
):
    """
    Stream and directly download the Instagram video file (MP4).
    This proxies the video stream directly so the user gets a file download attachment.
    """
    info = process_info_request(url)
    video_direct_url = info.get("video_url")
    video_id = info.get("id") or "video"
    filename = f"instagram_{video_id}.mp4"

    try:
        # Stream remote video
        headers = {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/122.0.0.0 Safari/537.36'
            )
        }
        req = requests.get(video_direct_url, stream=True, headers=headers, timeout=30)
        req.raise_for_status()

        def iterfile():
            for chunk in req.iter_content(chunk_size=64 * 1024):
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


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print(f"Starting Instagram Video Downloader API on http://0.0.0.0:{port} ...")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
