# filename: aiproxy.py
# GPL Mathias Aschhoff 2025

from fastapi import FastAPI, UploadFile, HTTPException, File, Query
import os
from pathlib import Path

app = FastAPI()


DEBUG = os.getenv("DEBUG", "false").lower() in ["1", "true", "yes"]



@app.post("/process_meter_image")
async def process_meter_image(file: UploadFile = File(...), mqtt_topic: str = Query(...)):

    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file is not an image.")


    try:

        image_bytes = await file.read()
        # --- Bild speichern ---
        save_dir = Path("img")
        save_dir.mkdir(parents=True, exist_ok=True)
    
        timestamp = datetime.datetime.now().isoformat().replace(":", "-").replace(".", "-")
        filename = f"img_{timestamp}.jpg"
        file_path = save_dir / filename
    
        with open(file_path, "wb") as f:
            f.write(image_bytes)

        
    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process image with Gemini: {e}")
