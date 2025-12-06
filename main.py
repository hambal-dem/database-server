from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from routers import media_storage
from routers import system_log
from routers import system_info

# system DB
from system_database import engine_sys, BaseSys
# models - import to ensure registration
import system_models

# routers
from routers import system_monitor, system_log

# in main.py
from routers.media_storage import short_redirect


app = FastAPI(title="Embedded Monitoring Server")

app.include_router(media_storage.router)
# create system tables if not exist
BaseSys.metadata.create_all(bind=engine_sys)

# include routers
app.include_router(system_monitor.router)
app.include_router(system_log.router)
app.include_router(system_info.router)

# static monitor
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/monitor")
def monitor():
    return FileResponse("static/monitor.html")

@app.get("/m/{code}")
def m_redirect(code: str):
    return RedirectResponse(url=f"/media/m/{code}")  # or directly lookup; but simpler: call DB
