from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import json
import os
import requests

app = FastAPI()

# Đặt API Key tùy ý để bảo mật server của bạn
API_KEY = "1e2e2fa7-c757-470a-8c55-c09d783aa6e5"
DATA_FILE = "data.json"

# URL Firebase Realtime Database của bạn
FIREBASE_URL = "https://roblox-bee-bot-default-rtdb.asia-southeast1.firebasedatabase.app/data.json"

# Hàm hỗ trợ đồng bộ dữ liệu sang Firebase
def sync_to_firebase(data: dict):
    try:
        requests.put(FIREBASE_URL, json=data, timeout=3)
    except Exception as e:
        print(f"[Lỗi Firebase Sync]: {e}")

# Khởi tạo file data nếu chưa có
if not os.path.exists(DATA_FILE):
    initial_data = {"minLevel": 1, "queue": []}
    with open(DATA_FILE, "w") as f:
        json.dump(initial_data, f)
    # Đồng bộ khởi tạo lên Firebase luôn
    sync_to_firebase(initial_data)

class QueueItem(BaseModel):
    jobid: str
    userid: str
    timestamp: int

class StorageData(BaseModel):
    minLevel: int
    queue: List[QueueItem]

def read_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def write_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

@app.get("/data")
def get_data(x_api_key: Optional[str] = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return read_data()

@app.put("/data")
def update_data(payload: StorageData, x_api_key: Optional[str] = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    data_dict = payload.dict()
    
    # 1. Lưu vào file data.json trên server như cũ
    write_data(data_dict)
    
    # 2. Đẩy một bản sao sang Firebase để xem Live trên Web
    sync_to_firebase(data_dict)
    
    return {"status": "success", "data": data_dict}
