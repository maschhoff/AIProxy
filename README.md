# AIProxy
ESP32 Cam AI Proxy

# RUN

export GOOGLE_API_KEY="sk-..."

export MQTT_BROKER="192.168.x.x"   # IP deines MQTT-Brokers

uvicorn aiproxy:app --host 0.0.0.0 --port 8000

# Docker
docker run -d \
  -p 8000:8000 \
  --name aiproxy \
  -e GOOGLE_API_KEY="sk-..."
  -e MQTT_BROKER="192.168.x.x" 
  knex666/aiproxy:latest-dev

