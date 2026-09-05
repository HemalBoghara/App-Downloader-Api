# 🚀 Render.com પર API હોસ્ટ કરવાની સરળ રીત (Step-by-Step Guide)

આ પ્રોજેક્ટ Render.com પર ફ્રીમાં લાઈવ હોસ્ટ કરવા માટે તૈયાર છે. નીચેના સરળ સ્ટેપ્સ ફોલો કરો:

---

## પદ્ધતિ ૧: GitHub દ્વારા Render પર Deploy કરવું (સૌથી સરળ અને શ્રેષ્ઠ)

### સ્ટેપ ૧: GitHub પર નવો Repository બનાવો
1. [GitHub.com](https://github.com) પર જાઓ અને લોગિન કરો.
2. ઉપર જમણી બાજુ **`+`** પર ક્લિક કરીને **`New repository`** પસંદ કરો.
3. Repository નું નામ આપો (દા.ત. `instagram-downloader-api`) અને **Create repository** બટન દબાવો.

---

### સ્ટેપ ૨: પ્રોજેક્ટ GitHub પર અપલોડ (Push) કરો
તમારા ટર્મિનલમાં આ કમાન્ડ્સ ચલાવો:

```bash
cd C:\Users\Hemal\.gemini\antigravity-ide\scratch\instagram_downloader_api

# તમારા GitHub repo ની લિંક અહી મૂકો:
git remote add origin https://github.com/<YOUR_USERNAME>/instagram-downloader-api.git
git branch -M main
git push -u origin main
```

---

### સ્ટેપ ૩: Render.com પર સર્વિસ બનાવો
1. [Render.com](https://dashboard.render.com/) પર જાઓ અને એકાઉન્ટ બનાવો / લોગિન કરો.
2. Dashboard માં **`New +`** બટન પર ક્લિક કરો અને **`Web Service`** પસંદ કરો.
3. તમારું GitHub એકાઉન્ટ કનેક્ટ કરી `instagram-downloader-api` repository પસંદ કરો (અથવા `render.yaml` Blueprint થી 1-Click deploy કરો).
4. નીચે મુજબ સેટિંગ્સ ભરો (જો મેન્યુઅલ સેટિંગ કરતા હોવ તો):
   - **Name**: `instagram-downloader-api`
   - **Language / Runtime**: `Python 3`
   - **Branch**: `main`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: `Free`
5. **`Deploy Web Service`** પર ક્લિક કરો!

---

## ⚡ 1-Click Blueprint પદ્ધતિ (Render Blueprint):
Render Dashboard માં **`New +`** -> **`Blueprint`** પસંદ કરી તમારું GitHub Repo સિલેક્ટ કરશો એટલે તે આપોઆપ આપણા બનાવેલા `render.yaml` માંથી બધું સેટિંગ્સ રીડ કરી લેશે અને ૨ મિનિટમાં એપ લાઈવ કરી દેશે!

---

## 🌐 લાઈવ થયા પછી કેવી રીતે વાપરવું:
તમને Render તરફથી એક ફ્રી લાઈવ URL મળશે, દા.ત. `https://instagram-downloader-api.onrender.com`

- **વેબ UI ટેસ્ટર**: `https://instagram-downloader-api.onrender.com/`
- **Swagger API Docs**: `https://instagram-downloader-api.onrender.com/docs`
- **API Info Endpoint**: `https://instagram-downloader-api.onrender.com/api/info?url=...`
- **API Download Endpoint**: `https://instagram-downloader-api.onrender.com/api/download?url=...`
