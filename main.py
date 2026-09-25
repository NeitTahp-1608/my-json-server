from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import json
import os

app = FastAPI()

# Đặt API Key tùy ý để bảo mật server của bạn
API_KEY = "1e2e2fa7-c757-470a-8c55-c09d783aa6e5"
DATA_FILE = "data.json"

# Khởi tạo file data nếu chưa có
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({"minLevel": 1, "queue": []}, f)

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
    write_data(data_dict)
    return {"status": "success", "data": data_dict}
