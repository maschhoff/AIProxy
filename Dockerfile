FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libgl1 \
    libsm6 \
    libxrender1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir ultralytics paddlepaddle paddleocr fastapi uvicorn[standard] opencv-python onnxruntime
COPY . /app
WORKDIR /app
EXPOSE 8000
CMD ["uvicorn", "aiproxy:app", "--host", "0.0.0.0", "--port", "8000"]
