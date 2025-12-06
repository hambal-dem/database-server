from sqlalchemy import Column, Integer, Float, DateTime, Index
from system_database import BaseSys
import datetime

class SystemLog(BaseSys):
    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, index=True)
    cpu = Column(Float, nullable=False)
    ram = Column(Float, nullable=False)
    upload = Column(Float, nullable=False)
    download = Column(Float, nullable=False)
    total_upload_mb = Column(Float, nullable=True)
    total_download_mb = Column(Float, nullable=True)
    storage = Column(Float, nullable=False)
    ts = Column(DateTime, default=datetime.datetime.utcnow, index=True)

# create index on timestamp for fast queries
Index("idx_systemlog_ts", SystemLog.ts)
