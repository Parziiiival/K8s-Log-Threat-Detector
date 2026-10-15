import os
import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

def train():
    raw_logs_path = "data/raw_logs1.csv"
    if not os.path.exists(raw_logs_path):
        print(f"Error: {raw_logs_path} not found. Run src/log_simulator.py first!")
        return

    print("Loading log data from disk...")
    df = pd.read_csv(raw_logs_path)

    # --- 1. FEATURE ENGINEERING ---
    # Create derived features to help the model spot abnormal packet behaviors
    df["bytes_per_packet"] = df["bytes"] / (df["packets"] + 1e-5)
    df["is_privileged_port"] = df["dst_port"].apply(lambda port: 1 if port < 1024 else 0)

    # Select numerical features for model input
    feature_cols = ["src_port", "dst_port", "packets", "bytes", "bytes_per_packet", "is_privileged_port"]
    X = df[feature_cols]

    # --- 2. FEATURE SCALING ---
    # Scale values so high numbers (like bytes) don't overpower lower ones (like port numbers)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # --- 3. MODEL TRAINING ---
    print("Training Isolation Forest Anomaly Detector...")
    # contamination = estimated ratio of anomalies (~5%)
    model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
    model.fit(X_scaled)

    # Predict on training set (-1 = Anomaly, 1 = Normal)
    df["prediction"] = model.predict(X_scaled)
    num_anomalies = (df["prediction"] == -1).sum()

    print(f"Training Complete! Flagged {num_anomalies} anomalies out of {len(df)} total logs.")

    # --- 4. SAVE ARTIFACTS ---
    os.makedirs("data", exist_ok=True)
    scaler_path = "data/scaler.joblib"
    model_path = "data/model.joblib"

    joblib.dump(scaler, scaler_path)
    joblib.dump(model, model_path)

    print(f"Saved scaler to '{scaler_path}'")
    print(f"Saved trained model to '{model_path}'")

if __name__ == "__main__":
    train()