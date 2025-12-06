from fastapi import APIRouter
from system_database import SessionSys
from sqlalchemy import func
from datetime import datetime, timedelta

router = APIRouter(prefix="/history", tags=["History"])

@router.get("/cpu")
def cpu_history(hours: int = 24):
    db = SessionSys()
    try:
        since = datetime.utcnow() - timedelta(hours=hours)
        q = db.query(func.avg(CpuLog.usage_percent).label('avg'),
                     func.min(CpuLog.usage_percent).label('min'),
                     func.max(CpuLog.usage_percent).label('max'))\
              .filter(CpuLog.ts >= since).one()
        return {"avg": q.avg, "min": q.min, "max": q.max}
    finally:
        db.close()
