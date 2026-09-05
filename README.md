# 🎥 Multi-Platform Video Downloader REST API (v2.0)

**Instagram**, **Facebook**, અને **YouTube** માંથી Reels, Shorts અને Videos ડાઉનલોડ કરવા માટેનું હાઈ-પરફોર્મન્સ Python REST API (FastAPI & yt-dlp).

---

## 🚀 Features (મુખ્ય સુવિધાઓ)
- 🎯 **3-in-1 Dedicated Support**: Instagram, Facebook અને YouTube ત્રણેયના અલગ-અલગ Endpoints.
- ✨ **Universal Smart Auto-Detect**: કોઈપણ લિંક નાખો, API પોતે જ પ્લેટફોર્મ ઓળખી લેશે.
- ⚡ **Direct Media Stream**: HD MP4 Direct Download Link, Thumbnail, Title, Duration, Author અને Views.
- 📥 **Direct File Streaming (`/download`)**: વિડીયો સીધો જ તમારા કમ્પ્યુટર કે ફોનમાં `.mp4` ફાઈલ તરીકે ડાઉનલોડ થાય છે.
- 💻 **Modern Web Tester UI**: Tabs સાથેનું ઇન્ટરેક્ટિવ વેબ ઇન્ટરફેસ.
- 📖 **Interactive Swagger Docs**: `/docs` પર સંપૂર્ણ API ટેસ્ટિંગ ટૂલ.

---

## 🔌 API Endpoints & Usage

### 1. 📸 Instagram Endpoints
- **Info**: `GET /api/instagram/info?url=https://www.instagram.com/reel/...`
- **Download**: `GET /api/instagram/download?url=https://www.instagram.com/reel/...`

### 2. 📘 Facebook Endpoints
- **Info**: `GET /api/facebook/info?url=https://www.facebook.com/reel/...` (or `https://fb.watch/...`)
- **Download**: `GET /api/facebook/download?url=https://www.facebook.com/reel/...`

### 3. ▶️ YouTube Endpoints
- **Info**: `GET /api/youtube/info?url=https://www.youtube.com/shorts/...` (or `https://youtu.be/...`)
- **Download**: `GET /api/youtube/download?url=https://www.youtube.com/shorts/...`

### 4. ✨ Universal Auto-Detect Endpoints
- **Info**: `GET /api/universal/info?url={ANY_SUPPORTED_URL}`
- **Download**: `GET /api/universal/download?url={ANY_SUPPORTED_URL}`

---

## 📦 JSON Response Example

```json
{
  "success": true,
  "platform": "youtube",
  "id": "dQw4w9WgXcQ",
  "title": "Rick Astley - Never Gonna Give You Up",
  "description": "The official video for...",
  "uploader": "Rick Astley",
  "uploader_id": "RickAstleyVEVO",
  "thumbnail": "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
  "duration": 213.0,
  "view_count": 1500000000,
  "like_count": 16000000,
  "video_url": "https://rr3---sn-....googlevideo.com/videoplayback?...",
  "width": 1920,
  "height": 1080,
  "ext": "mp4",
  "source_url": "https://youtu.be/dQw4w9WgXcQ"
}
```

---

## 🐍 Client Integration Examples

### Python:
```python
import requests

api_url = "http://127.0.0.1:8000/api/universal/info"
video_url = "https://www.youtube.com/shorts/example123"

res = requests.get(api_url, params={"url": video_url}).json()
if res.get("success"):
    print(f"Platform: {res['platform']}")
    print(f"Title: {res['title']}")
    print(f"Direct MP4 Link: {res['video_url']}")
```

### JavaScript:
```javascript
async function fetchMedia(url) {
    const res = await fetch(`http://127.0.0.1:8000/api/universal/info?url=${encodeURIComponent(url)}`);
    const data = await res.json();
    console.log(data);
}
```

---

## 🚀 Local Run:
```bash
pip install -r requirements.txt
python main.py
```
- Web UI: `http://127.0.0.1:8000`
- Swagger Docs: `http://127.0.0.1:8000/docs`
