# AIProxy
ESP32 Cam AI Proxy

# RUN

export OPENAI_API_KEY="sk-..."

export MQTT_BROKER="192.168.x.x"   # IP deines MQTT-Brokers

uvicorn aiproxy:app --host 0.0.0.0 --port 8000
