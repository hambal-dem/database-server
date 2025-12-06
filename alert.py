from datetime import datetime, timedelta
from system_database import SessionSys
from system_models import CpuLog
from alert_models import Alert

def check_cpu_alert():
    db = SessionSys()
    try:
        cutoff = datetime.utcnow() - timedelta(minutes=5)
        logs = db.query(CpuLog).filter(CpuLog.ts >= cutoff).all()

        if logs:
            avg_cpu = sum([l.usage_percent for l in logs]) / len(logs)
            if avg_cpu > 90:
                db.add(Alert(level="CRITICAL", title="CPU overload", message=f"CPU avg: {avg_cpu}"))
                db.commit()
    finally:
        db.close()
