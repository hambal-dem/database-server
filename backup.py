import shutil
import datetime
from config import SYSTEM_DB_PATH

def backup_logs():
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_path = f"../database/backups/system_logs_{timestamp}.db"
    shutil.copyfile(SYSTEM_DB_PATH, backup_path)
