from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import subprocess, json, uuid, os

app = FastAPI()

# CORS (frontend access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "API running"}

# Extract formats
@app.post("/extract")
def extract(data: dict):
    url = data.get("url")

    try:
        result = subprocess.run(
            ["yt-dlp", "-J", url],
            capture_output=True,
            text=True
        )

        info = json.loads(result.stdout)

        formats = []
        for f in info.get("formats", []):
            if f.get("ext") == "mp4" and f.get("format_id"):
                formats.append({
                    "id": f.get("format_id"),
                    "quality": f.get("format_note") or f.get("height"),
                    "ext": f.get("ext")
                })

        return {"formats": formats[:10]}

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


# Download video
@app.get("/download")
def download(url: str, format_id: str):
    try:
        filename = f"{uuid.uuid4()}.mp4"

        subprocess.run([
            "yt-dlp",
            "-f", format_id,
            url,
            "-o", filename
        ])

        return FileResponse(
            path=filename,
            media_type="video/mp4",
            filename="video.mp4"
        )

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
