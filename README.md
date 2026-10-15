
# AI-Powered K8s Network & Log Threat Detector

[![Live API](https://img.shields.io/badge/Render-Live%20API-success?style=flat-square&logo=render)](https://k8s-log-threat-detector.onrender.com)
[![FastAPI Docs](https://img.shields.io/badge/FastAPI-Interactive%20Docs-blue?style=flat-square&logo=fastapi)](https://k8s-log-threat-detector.onrender.com/docs)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?style=flat-square&logo=docker)](https://github.com/YOUR_USERNAME/k8s-log-threat-detector)

An end-to-end AI SecOps microservice pipeline that detects anomalous network traffic patterns (such as port scans and data exfiltration attempts) using unsupervised Machine Learning, containerized with Docker, and monitored via Prometheus and Grafana telemetry.

> **🌐 Live Cloud Deployment**  
> The API container is automatically deployed and running live on Render:  
> **Live API Base:** [https://k8s-log-threat-detector.onrender.com](https://k8s-log-threat-detector.onrender.com)  
> **Interactive Swagger Docs:** [https://k8s-log-threat-detector.onrender.com/docs](https://k8s-log-threat-detector.onrender.com/docs)  
> **Prometheus Metrics Endpoint:** [https://k8s-log-threat-detector.onrender.com/metrics](https://k8s-log-threat-detector.onrender.com/metrics)

---

## Architecture Overview

```text
┌─────────────────────────────────────────────────────────────┐
│                      BACKEND CONTAINER                      │
│                                                             │
│   ┌─────────────────────┐       ┌───────────────────────┐   │
│   │   FastAPI Server    │ ──►   │ Isolation Forest Model│   │
│   │   (src/app.py)      │       │ (data/model.joblib)   │   │
│   └──────────┬──────────┘       └───────────────────────┘   │
│              │ Exposes /metrics                             │
└──────────────┼──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│                   TELEMETRY & OBSERVABILITY                 │
│                                                             │
│   ┌─────────────────────┐       ┌───────────────────────┐   │
│   │     Prometheus      │ ──►   │   Grafana Dashboard   │   │
│   │ (Metrics Collector) │       │ (Visual Interface)    │   │
│   └─────────────────────┘       └───────────────────────┘   │
└─────────────────────────────────────────────────────────────┘

### Key Features
* **Unsupervised Anomaly Detection:** Uses `scikit-learn`'s `IsolationForest` to flag high-volume data exfiltration and abnormal port behavior without needing historical labels.
* **Feature Engineering:** Computes dynamic metrics (`bytes_per_packet`, privileged destination port identification) on raw network log inputs.
* **REST API Microservice:** Built with `FastAPI` and validated with `Pydantic` schemas for low-latency JSON evaluation.
* **Prometheus Telemetry:** Exposes custom counters (`threat_anomalies_detected_total`, `total_log_requests_processed`) on a standard `/metrics` endpoint.
* **Multi-Container Orchestration:** Uses `Docker` and `Docker Compose` to connect the Python API, Prometheus scraper, and Grafana UI on an internal container network.

---

## Directory Structure

```text
k8s-log-threat-detector/
│
├── data/                       # Pre-generated logs and trained ML artifacts
│   ├── raw_logs.csv            # Synthetic traffic logs
│   ├── scaler.joblib           # Feature standardizer rules
│   └── model.joblib            # Trained Isolation Forest model
│
├── src/                        # Python codebase
│   ├── log_simulator.py        # Generates synthetic traffic logs
│   ├── train_model.py          # Performs feature extraction and model fitting
│   └── app.py                  # FastAPI server with Prometheus instrumentation
│
├── monitoring/                 # Monitoring configurations
│   └── prometheus.yml          # Prometheus scrape job targeting the API
│
├── .gitignore                  # Git exclusions
├── Dockerfile                  # Container build recipe for Python microservice
├── docker-compose.yml          # Multi-container orchestration stack
└── requirements.txt            # Python dependencies
```

---

## Prerequisites

Ensure you have the following installed locally:
* **Python 3.11+**
* **Git**
* **Docker Desktop** (with Docker Compose enabled)

---

## Quick Start Guide

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/k8s-log-threat-detector.git
cd k8s-log-threat-detector
```

### 2. Set Up Python Environment & Dependencies
```bash
python -m venv .venv
# On Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# On macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Generate Synthetic Network Logs
Simulate 1,000 normal browsing logs mixed with 50 malicious attack patterns:
```bash
python src/log_simulator.py
```
*Output:* Generates `data/raw_logs.csv`.

### 4. Train the AI Model
Extract engineered features and train the Isolation Forest model:
```bash
python src/train_model.py
```
*Output:* Creates `data/scaler.joblib` and `data/model.joblib`.

---

## Running the Containerized Stack

Launch the API backend, Prometheus collector, and Grafana dashboard together using Docker Compose.

### 1. Build and Start Containers
```bash
docker-compose up --build
```

### 2. Verify Running Services

| Service | Access URL | Purpose |
| :--- | :--- | :--- |
| **FastAPI Docs** | `http://localhost:8000/docs` | Interactive API sandbox for manual testing |
| **Prometheus** | `http://localhost:9090` | Raw metrics database & scraper status |
| **Grafana** | `http://localhost:3000` | Visual security metrics dashboard |

*(Grafana Login: Default username `admin` / password `admin`)*

---

## Grafana Dashboard Setup

1. Log into Grafana at `http://localhost:3000`.
2. Go to **Connections** > **Data sources** > **Add data source** > Select **Prometheus**.
3. Set the Prometheus Server URL to:
   ```text
   http://prometheus:9090
   ```
   *(Note: Uses Docker's internal container DNS).*
4. Click **Save & test**.
5. Create a **New Dashboard** > **Add Visualization** > Select your **Prometheus** data source.
6. Enter either of the following queries:
   * **Cumulative Threat Count:** `threat_anomalies_detected_total`
   * **Real-time Threat Rate (per min):** `increase(threat_anomalies_detected_total[1m])`
7. Set the top-right time range picker to **Last 15 minutes** and click **Save**.

---

## Testing & Threat Injection

Send real-time attack payloads to trigger model alerts and watch the Grafana dashboard spike.

Open a separate terminal window and run:

```powershell
python -c "import requests, time, random; [requests.post('http://localhost:8000/analyze', json={'src_port': random.randint(1024,65535), 'dst_port': 9000, 'packets': 1200, 'bytes': 2500000}) or time.sleep(0.5) for _ in range(10)]"
```

### Expected Output Payload (`/analyze`):
```json
{
  "status": "THREAT_DETECTED",
  "anomaly_score": -0.1842,
  "details": "Anomalous network activity detected by Isolation Forest."
}
```

---

## API Documentation Reference

### `POST /analyze`
Analyzes a single network telemetry log and returns threat status.

* **Request Body:**
```json
{
  "src_port": 52140,
  "dst_port": 22,
  "packets": 1,
  "bytes": 40
}
```

* **Response (Normal Traffic):**
```json
{
  "status": "NORMAL",
  "anomaly_score": 0.0421
}
```

### `GET /metrics`
Exposes application metrics formatted for Prometheus scraping.

---

## Security Considerations

* **False Positives vs Time-Windowing:** Single low-byte logs (e.g., single pings or stealth port scans) look similar to normal traffic at an isolated record level. Production implementations aggregate logs across rolling time windows (e.g., unique destination ports hit per 10 seconds).
* **Non-Root Containers:** Production Docker images should run under non-root permissions to enforce least-privilege principles.
