# install (lokal): pip install ultralytics paddlepaddle paddleocr fastapi uvicorn[standard] opencv-python
from ultralytics import YOLO
from paddleocr import PaddleOCR
import cv2, numpy as np, re
from fastapi import FastAPI, UploadFile, File
import cv2, numpy as np
app = FastAPI()

detector = YOLO("weights/display_yolov8n.pt")  # dein feingetuntes ROI-Modell
ocr = PaddleOCR(lang='en', det=False, rec=True) # nur Rekognition

def read_meter(img_bgr):
    # 1) ROI-Detektion
    results = detector.predict(source=img_bgr, imgsz=640, conf=0.25, verbose=False)
    if not results or len(results[0].boxes) == 0:
        return {"text": None, "conf": 0.0}
    # beste Box
    box = results[0].boxes[results[0].boxes.conf.argmax()]
    x1,y1,x2,y2 = map(int, box.xyxy[0].tolist())
    crop = img_bgr[max(0,y1):y2, max(0,x1):x2]

    # 2) Preprocess
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 7, 50, 50)
    crop_proc = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    # 3) OCR
    ocr_res = ocr.ocr(crop_proc, cls=False)
    text = "".join([x[1][0] for line in ocr_res for x in line])
    text = text.strip().replace(',', '.')
    text = re.sub(r'[^0-9\.]', '', text)

    # 4) Plausibilisierung (Beispiel)
    if text.count('.') > 1:
        # nimm die wahrscheinlichste dezimaltrennung: letzte Punktposition
        left, right = text.rsplit('.', 1)
        text = re.sub(r'\.', '', left) + '.' + right
    return {"text": text, "conf": float(box.conf[0])}


@app.post("/process_meter_image")
async def predict(file: UploadFile = File(...)):
    data = await file.read()
    img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    out = read_meter(img)
    return out
