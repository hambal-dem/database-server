import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))
DB_DIR = os.path.join(ROOT_DIR, "database")
os.makedirs(DB_DIR, exist_ok=True)
BASE_URL = "http://127.0.0.1:8000"
# Path DB untuk system logs
SYSTEM_DB_PATH = os.path.join(DB_DIR, "system_logs.db")
SYSTEM_DATABASE_URL = f"sqlite:///{SYSTEM_DB_PATH}"

# API key untuk endpoint /system/log — ganti dengan yang aman
SYSTEM_API_KEY = "12345"
