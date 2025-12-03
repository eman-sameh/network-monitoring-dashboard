from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
import pandas as pd
import numpy as np
from datetime import datetime
from tensorflow.keras.models import load_model
import threading
import time
from fastapi.staticfiles import StaticFiles
import uvicorn

# ---------------- Config ----------------
MODEL_FILE = "my_model.keras"
CSV_FILE = "live_simulation.csv"
TIMESTEPS = 10
MAX_ROWS = 20

# Load model & CSV
model = load_model(MODEL_FILE)
live_df = pd.read_csv(CSV_FILE)
FEATURE_COLS = [
    'Destination Port', 'Flow Duration', 'Total Fwd Packets', 'Total Length of Fwd Packets',
    'Fwd Packet Length Max', 'Fwd Packet Length Min', 'Fwd Packet Length Mean', 'Fwd Packet Length Std',
    'Bwd Packet Length Max', 'Bwd Packet Length Min', 'Bwd Packet Length Mean', 'Bwd Packet Length Std',
    'Flow Bytes/s', 'Flow Packets/s', 'Flow IAT Mean', 'Flow IAT Std', 'Flow IAT Max',
    'Fwd IAT Total', 'Fwd IAT Mean', 'Fwd IAT Std', 'Fwd IAT Max', 'Fwd IAT Min',
    'Bwd IAT Total', 'Bwd IAT Mean', 'Bwd IAT Std', 'Bwd IAT Max', 'Bwd IAT Min',
    'Fwd Header Length', 'Bwd Header Length', 'Fwd Packets/s', 'Bwd Packets/s', 'Min Packet Length',
    'Max Packet Length', 'Packet Length Mean', 'Packet Length Std', 'Packet Length Variance',
    'FIN Flag Count', 'PSH Flag Count', 'ACK Flag Count', 'URG Flag Count', 'Down/Up Ratio',
    'Average Packet Size', 'Subflow Fwd Bytes', 'Init_Win_bytes_forward', 'Init_Win_bytes_backward',
    'act_data_pkt_fwd', 'min_seg_size_forward', 'Active Mean', 'Active Max', 'Active Min',
    'Idle Mean', 'Idle Max', 'Idle Min', 'Bytes per Packet', 'Direction Imbalance', 'Flow IAT Ratio',
    'Packet Length Variability', 'Active Idle Ratio', 'Fwd Bwd Packet Length Ratio', 'Flow IAT Range',
    'Fwd IAT Range', 'Bwd IAT Range', 'Total Flag Count'
]

# ---------------- App & CORS ----------------
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/icons", StaticFiles(directory="icons"), name="icons")

@app.get("/")
def read_index():
    return FileResponse("index.html")

# ---------------- Shared State ----------------
sequence_buffer = []
global_count = 0
total_attacks = 0
total_normal = 0
local_df = pd.DataFrame(columns=FEATURE_COLS + ['timestamp','label','score'])
global_df = pd.DataFrame(columns=FEATURE_COLS + ['timestamp','label','score'])

# ---------------- Background Prediction Loop ----------------
def live_loop():
    global sequence_buffer, local_df, global_df, global_count, total_attacks, total_normal
    for row in live_df[FEATURE_COLS].values:
        sequence_buffer.append(row)
        if len(sequence_buffer) == TIMESTEPS:
            seq = np.array(sequence_buffer).reshape(1, TIMESTEPS, len(FEATURE_COLS))
            pred = float(model.predict(seq, verbose=0)[0][0])
            label = "ATTACK" if pred > 0.5 else "NORMAL"
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            global_count += 1
            if label == "ATTACK":
                total_attacks += 1
            else:
                total_normal += 1

            entry = {col: float(val) for col, val in zip(FEATURE_COLS, row)}
            entry.update({"timestamp": timestamp, "label": label, "score": pred})

            local_df = pd.concat([local_df, pd.DataFrame([entry])], ignore_index=True)
            if len(local_df) > MAX_ROWS:
                local_df = local_df.tail(MAX_ROWS).reset_index(drop=True)

            global_df = pd.concat([global_df, pd.DataFrame([entry])], ignore_index=True)

            sequence_buffer.pop(0)

        time.sleep(0.5)

threading.Thread(target=live_loop, daemon=True).start()

# ---------------- API Endpoint ----------------
@app.get("/data")
def get_data():
    if local_df.empty:
        return JSONResponse({
            "total": 0, "attacks": 0, "normal": 0, "most_port": "-", "most_port_hits": 0,
            "latest": {}, "table": [], "port_attack_counts": {}
        })

    port = global_df['Destination Port'].mode()[0]
    hits = (global_df['Destination Port'] == port).sum()
    latest = local_df.iloc[-1].to_dict()
    table = local_df.to_dict(orient='records')

    # NEW: Attack-only port count
    attack_df = global_df[global_df["label"] == "ATTACK"]
    port_counts = attack_df["Destination Port"].value_counts().to_dict()

    return JSONResponse({
        "total": int(global_count),
        "attacks": int(total_attacks),
        "normal": int(total_normal),
        "most_port": int(port),
        "most_port_hits": int(hits),
        "latest": latest,
        "table": table,
        "port_attack_counts": port_counts
    })