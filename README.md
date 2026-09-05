# 📸 Instagram Video Downloader API (Python)

ઇન્સ્ટાગ્રામ (Instagram Reels, Videos, IGTV અને Posts) માંથી વિડીયો સરળતાથી ડાઉનલોડ કરવા માટે **FastAPI** અને **yt-dlp** પર આધારિત હાઈ-પરફોર્મન્સ REST API.

---

## 🚀 Features (મુખ્ય સુવિધાઓ)
- ⚡ **Super Fast & Lightweight**: FastAPI આધારિત અસિંક આર્કિટેક્ચર.
- 🎯 **All-in-One Support**: Reels, Posts, Videos અને IGTV સપોર્ટ.
- 📦 **Direct Media Extraction**: HD MP4 Direct Download Link, Thumbnail, Title, Duration, Author, Views કાઢે છે.
- 📥 **Direct File Streaming (`/api/download`)**: બ્રાઉઝર કે અન્ય એપ્લિકેશનમાં સીધી જ `.mp4` ફાઈલ ડાઉનલોડ થાય.
- 💻 **Modern Web Tester UI**: લિંક પેસ્ટ કરીને તરત જ વિડીયો પ્લે અને ડાઉનલોડ ટેસ્ટ કરી શકાય.
- 📖 **Interactive Swagger UI Docs**: `/docs` પર સંપૂર્ણ API ટેસ્ટિંગ ટૂલ.

---

## 🛠️ Installation & Setup (કેવી રીતે શરૂ કરવું)

### 1. Requirements ઇન્સ્ટોલ કરો:
```bash
cd C:\Users\Hemal\.gemini\antigravity-ide\scratch\instagram_downloader_api
pip install -r requirements.txt
```

### 2. API સર્વર રન કરો:
```bash
python main.py
```
અથવા Uvicorn થી રન કરો:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

સર્વર શરૂ થયા પછી નીચેની લિંક્સ ખોલો:
- **Web UI & Tester**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Swagger API Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 🔌 API Endpoints & Usage (API નો ઉપયોગ કેવી રીતે કરવો)

### 1. Get Video Information (Metadata & Direct Link)

#### **Endpoint:** `GET /api/info`
```http
GET /api/info?url=https://www.instagram.com/reel/C8.../
```

#### **અથવા `POST /api/info`:**
```bash
curl -X POST "http://127.0.0.1:8000/api/info" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://www.instagram.com/reel/C8..."}'
```

#### **Response (JSON Output Example):**
```json
{
  "success": true,
  "id": "C8AbCdEfGh",
  "title": "Amazing Nature Reel",
  "description": "Beautiful sunset in the mountains #nature",
  "uploader": "nature_lover",
  "uploader_id": "nature_lover",
  "thumbnail": "https://instagram.f...net/...jpg",
  "duration": 15.4,
  "view_count": 125000,
  "like_count": 8450,
  "comment_count": 120,
  "video_url": "https://instagram.f...net/...mp4",
  "width": 1080,
  "height": 1920,
  "ext": "mp4",
  "source_url": "https://www.instagram.com/reel/C8.../"
}
```

---

### 2. Direct Video Download Stream (સીધો વિડીયો ફાઇલ ડાઉનલોડ કરવા)

#### **Endpoint:** `GET /api/download`
```http
GET /api/download?url=https://www.instagram.com/reel/C8.../
```
આ URL ને બ્રાઉઝરમાં ખોલવાથી અથવા તમારા એપ માં કોલ કરવાથી સીધી `instagram_<id>.mp4` ફાઈલ ડાઉનલોડ થશે.

---

## 🐍 Client Integration Examples

### Python (using `requests`):
```python
import requests

api_url = "http://127.0.0.1:8000/api/info"
instagram_link = "https://www.instagram.com/reel/C8abc123/"

response = requests.get(api_url, params={"url": instagram_link})
data = response.json()

if data.get("success"):
    print(f"Title: {data['title']}")
    print(f"Direct MP4 Link: {data['video_url']}")
    
    # વિડીયો ડાઉનલોડ કરી સેવ કરવા માટે:
    video_bytes = requests.get(data['video_url']).content
    with open(f"{data['id']}.mp4", "wb") as f:
        f.write(video_bytes)
    print("Video successfully downloaded!")
```

### JavaScript / Frontend (Fetch API):
```javascript
async function downloadInstagramVideo(url) {
    const res = await fetch(`http://127.0.0.1:8000/api/info?url=${encodeURIComponent(url)}`);
    const data = await res.json();
    if (data.success) {
        console.log("Video Direct URL:", data.video_url);
        window.open(data.video_url, '_blank');
    }
}
```
