from datetime import datetime, timedelta
from system_database import SessionSys
from system_models import CpuLog, MemoryLog, NetworkLog, StorageLog

def rotate_logs():
    db = SessionSys()
    try:
        cutoff = datetime.utcnow() - timedelta(hours=24)
        tables = [CpuLog, MemoryLog, NetworkLog, StorageLog]

        for table in tables:
            db.query(table).filter(table.ts < cutoff).delete()
        
        db.commit()
    finally:
        db.close()
