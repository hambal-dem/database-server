from fastapi import APIRouter, BackgroundTasks, Header, HTTPException
from pydantic import BaseModel
from typing import Optional
from system_database import SessionLocalSys
from system_models import SystemLog
from config import SYSTEM_API_KEY
import datetime

router = APIRouter(tags=["SystemLogs"])

class LogPayload(BaseModel):
    cpu: float
    ram: float
    upload: float
    download: float
    storage: float
    total_upload_mb: Optional[float] = None
    total_download_mb: Optional[float] = None

def save_log(payload: dict):
    db = SessionLocalSys()
    try:
        entry = SystemLog(
            cpu=payload["cpu"],
            ram=payload["ram"],
            upload=payload["upload"],
            download=payload["download"],
            storage=payload["storage"],
            total_upload_mb=payload.get("total_upload_mb"),
            total_download_mb=payload.get("total_download_mb"),
            ts=datetime.datetime.utcnow(),
        )
        db.add(entry)
        db.commit()
    finally:
        db.close()

@router.post("/system/log")
def post_log(
    background_tasks: BackgroundTasks,
    payload: LogPayload,
    x_api_key: str = Header(None)
):
    if x_api_key != SYSTEM_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    background_tasks.add_task(save_log, payload.dict())
    return {"status": "queued"}
