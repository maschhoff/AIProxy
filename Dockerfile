FROM python:3.11-slim
RUN pip install --no-cache-dir ultralytics paddlepaddle paddleocr fastapi uvicorn[standard] opencv-python onnxruntime
COPY . /app
WORKDIR /app
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
