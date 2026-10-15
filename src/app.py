import joblib
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from prometheus_client import Counter, make_asgi_app

# Initialize FastAPI App
app = FastAPI(title="K8s Log Threat Detector API")

# Load model and scaler artifacts from Step 4
try:
    scaler = joblib.load("data/scaler.joblib")
    model = joblib.load("data/model.joblib")
except Exception as e:
    raise RuntimeError("Model or scaler not found in data/. Run src/train_model.py first!") from e

# Define Prometheus Metrics
ANOMALY_COUNTER = Counter("threat_anomalies_detected_total", "Total count of detected threat anomalies")
REQUEST_COUNTER = Counter("total_log_requests_processed", "Total log records processed")

# Input Data Schema Validation
class LogPayload(BaseModel):
    src_port: int
    dst_port: int
    packets: int
    bytes: int

@app.get("/")
def root():
    return {"status": "online", "message": "K8s Log Threat Detector API is running."}

@app.post("/analyze")
def analyze_log(payload: LogPayload):
    REQUEST_COUNTER.inc()

    # Feature engineering (must match train_model.py)
    bytes_per_packet = payload.bytes / (payload.packets + 1e-5)
    is_privileged = 1 if payload.dst_port < 1024 else 0

    features = np.array([[
        payload.src_port,
        payload.dst_port,
        payload.packets,
        payload.bytes,
        bytes_per_packet,
        is_privileged
    ]])

    # Scale features and run inference
    scaled_features = scaler.transform(features)
    prediction = model.predict(scaled_features)[0]  # -1 = Anomaly, 1 = Normal
    anomaly_score = float(model.decision_function(scaled_features)[0])

    if prediction == -1:
        ANOMALY_COUNTER.inc()
        return {
            "status": "THREAT_DETECTED",
            "anomaly_score": anomaly_score,
            "details": "Anomalous network activity detected by Isolation Forest."
        }

    return {
        "status": "NORMAL",
        "anomaly_score": anomaly_score
    }

# Mount Prometheus /metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)