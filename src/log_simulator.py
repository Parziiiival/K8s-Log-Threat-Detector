import os

try:
    import numpy as np  # type: ignore[import-not-found]
    import pandas as pd  # type: ignore[import-not-found]
except ImportError as exc:
    raise ImportError(
        "Missing required dependencies. Install them with: pip install numpy pandas"
    ) from exc

# Set seed so generated numbers are reproducible
np.random.seed(42)

def generate_logs(num_normal=1000, num_attacks=50):
    print("Generating synthetic network logs...")

    # --- 1. NORMAL TRAFFIC ---
    # Standard web browsing (HTTP/HTTPS ports 80 & 443, small packet counts & byte sizes)
    normal_data = {
        "src_port": np.random.randint(1024, 65535, size=num_normal),
        "dst_port": np.random.choice([80, 443], size=num_normal),
        "packets": np.random.randint(1, 20, size=num_normal),
        "bytes": np.random.randint(64, 2000, size=num_normal),
    }

    # --- 2. ATTACK TRAFFIC ---
    # Mix of Port Scans (single packets to SSH/RDP ports) and Data Exfiltration (massive byte dumps)
    attack_src_ports = np.random.randint(1024, 65535, size=num_attacks)
    attack_dst_ports = np.random.choice([22, 23, 3389, 8080, 9000], size=num_attacks)
    attack_packets = np.random.choice([1, 1, 1, 300, 800], size=num_attacks)
    attack_bytes = np.random.choice([40, 40, 40, 500000, 1500000], size=num_attacks)

    attack_data = {
        "src_port": attack_src_ports,
        "dst_port": attack_dst_ports,
        "packets": attack_packets,
        "bytes": attack_bytes,
    }

    # --- 3. COMBINE INTO PANDAS DATAFRAME ---
    df_normal = pd.DataFrame(normal_data)
    df_attack = pd.DataFrame(attack_data)
    
    # Concatenate normal and attack traffic
    df = pd.concat([df_normal, df_attack], ignore_index=True)

    # Shuffle the dataset so attacks are randomly mixed in
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)

    # --- 4. SAVE TO DISK ---
    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "raw_logs1.csv")
    
    # Save as CSV without index column
    df.to_csv(output_path, index=False)
    print(f"Successfully generated {len(df)} total logs and saved to '{output_path}'!")

if __name__ == "__main__":
    generate_logs()