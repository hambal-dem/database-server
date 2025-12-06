import psutil
import shutil
import time
from fastapi import APIRouter

router = APIRouter(prefix="/system", tags=["System Info"])


@router.get("/cpu")
def cpu_info():
    return {
        "cpu_usage_percent": psutil.cpu_percent(interval=1),
        "cpu_core_count": psutil.cpu_count(logical=True),
        "cpu_core_physical": psutil.cpu_count(logical=False)
    }


@router.get("/memory")
def memory_info():
    mem = psutil.virtual_memory()
    return {
        "total_ram_gb": round(mem.total / (1024 ** 3), 2),
        "used_ram_gb": round(mem.used / (1024 ** 3), 2),
        "free_ram_gb": round(mem.available / (1024 ** 3), 2),
        "memory_usage_percent": mem.percent
    }


@router.get("/storage")
def storage_info():
    usage = shutil.disk_usage(".")
    return {
        "total_storage_gb": round(usage.total / (1024 ** 3), 2),
        "used_storage_gb": round(usage.used / (1024 ** 3), 2),
        "free_storage_gb": round(usage.free / (1024 ** 3), 2),
        "storage_usage_percent": round((usage.used / usage.total) * 100, 2)
    }


@router.get("/network")
def network_info():
    net1 = psutil.net_io_counters()
    time.sleep(1)
    net2 = psutil.net_io_counters()

    upload_speed = net2.bytes_sent - net1.bytes_sent
    download_speed = net2.bytes_recv - net1.bytes_recv

    return {
        "total_upload_mb": round(net2.bytes_sent / (1024 ** 2), 2),
        "total_download_mb": round(net2.bytes_recv / (1024 ** 2), 2),
        "upload_speed_kb_s": round(upload_speed / 1024, 2),
        "download_speed_kb_s": round(download_speed / 1024, 2)
    }
