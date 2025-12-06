# server/media_models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Index
from system_database import BaseSys
import datetime

class MediaFile(BaseSys):
    __tablename__ = "media_files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    filepath = Column(String, nullable=False)
    filetype = Column(String, nullable=False)  # "image" or "video"
    size_mb = Column(Float, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)
    # NEW FIELDS
    public = Column(Boolean, default=True, nullable=False)            # public or private
    password_hash = Column(String, nullable=True)                     # if protected
    short_code = Column(String, nullable=True, unique=True)           # base62 short code
    thumbnail_path = Column(String, nullable=True)                    # generated thumbnail

# index for faster queries by upload time
Index("idx_media_uploaded_at", MediaFile.uploaded_at)
