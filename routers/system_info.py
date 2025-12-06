import psutil
import shutil
from fastapi import APIRouter

router = APIRouter()

# CPU =====================================================================
@router.get("/system/cpu")
def get_cpu_usage():
    cpu_percent = psutil.cpu_percent(interval=0.5)
    return {"cpu_usage_percent": cpu_percent}

# MEMORY ==================================================================
@router.get("/system/memory")
def get_memory_usage():
    mem = psutil.virtual_memory()
    return {"memory_usage_percent": mem.percent}

# NETWORK =================================================================
last_io = psutil.net_io_counters()
last_upload = last_io.bytes_sent
last_download = last_io.bytes_recv

@router.get("/system/network")
def get_network_usage():
    global last_upload, last_download

    current = psutil.net_io_counters()
    upload_speed = (current.bytes_sent - last_upload) / 1024  # KB/s
    download_speed = (current.bytes_recv - last_download) / 1024  # KB/s

    last_upload = current.bytes_sent
    last_download = current.bytes_recv

    return {
        "upload_speed_kb_s": round(upload_speed, 2),
        "download_speed_kb_s": round(download_speed, 2)
    }

# STORAGE =================================================================
@router.get("/system/storage")
def get_storage_usage():
    disk = shutil.disk_usage("C:\\")  # partisi utama
    used_percent = round((disk.used / disk.total) * 100, 2)
    return {"storage_usage_percent": used_percent}
