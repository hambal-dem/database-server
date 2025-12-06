# server/routers/media_storage.py
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Query
from fastapi.responses import FileResponse, RedirectResponse
from system_database import SessionLocalSys
from media_models import MediaFile
from media_utils import create_image_thumbnail, create_video_thumbnail, base62_encode, hash_password
import os, shutil
from config import SYSTEM_API_KEY, BASE_URL  # BASE_URL optional; or use hardcoded

router = APIRouter(prefix="/media", tags=["MediaStorage"])

MEDIA_ROOT = "media_storage"
IMAGE_DIR = os.path.join(MEDIA_ROOT, "images")
VIDEO_DIR = os.path.join(MEDIA_ROOT, "videos")
THUMB_DIR = os.path.join(MEDIA_ROOT, "thumbs")

os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(THUMB_DIR, exist_ok=True)

def save_to_db(db, filename, filepath, filetype, size_mb, public=True, password_hash=None, thumbnail_path=None):
    entry = MediaFile(
        filename=filename,
        filepath=filepath,
        filetype=filetype,
        size_mb=size_mb,
        public=public,
        password_hash=password_hash,
        thumbnail_path=thumbnail_path
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    # generate short code after we have id
    entry.short_code = base62_encode(entry.id)
    db.commit()
    db.refresh(entry)
    return entry

@router.post("/upload")
async def upload_media(background_tasks: BackgroundTasks,
                       file: UploadFile = File(...),
                       public: bool = Query(True),
                       password: str | None = Query(None)):
    ext = file.filename.split(".")[-1].lower()
    if ext in ["jpg", "jpeg", "png", "webp"]:
        folder = IMAGE_DIR
        filetype = "image"
    elif ext in ["mp4", "mov", "avi", "mkv", "webm"]:
        folder = VIDEO_DIR
        filetype = "video"
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    save_path = os.path.join(folder, file.filename)
    # avoid overwrite: add random suffix if exists
    if os.path.exists(save_path):
        base, extn = os.path.splitext(file.filename)
        save_path = os.path.join(folder, f"{base}_{os.urandom(4).hex()}{extn}")

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    size_mb = round(os.path.getsize(save_path) / (1024 ** 2), 2)
    db = SessionLocalSys()
    try:
        pwd_hash = hash_password(password) if password else None
        # create DB entry
        entry = save_to_db(db, os.path.basename(save_path), save_path, filetype, size_mb, public, pwd_hash, None)
    finally:
        db.close()

    # generate thumbnail in background
    def gen_thumb(eid, path, ftype):
        db2 = SessionLocalSys()
        try:
            thumb_name = f"thumb_{eid}.jpg"
            thumb_path = os.path.join(THUMB_DIR, thumb_name)
            if ftype == "image":
                create_image_thumbnail(path, thumb_path)
            else:
                # try ffmpeg
                t = create_video_thumbnail(path, thumb_path)
                if not t:
                    # fallback: do nothing
                    pass
            # update DB path
            item = db2.query(MediaFile).get(eid)
            if item:
                item.thumbnail_path = thumb_path if os.path.exists(thumb_path) else None
                db2.commit()
        finally:
            db2.close()

    background_tasks.add_task(gen_thumb, entry.id, save_path, filetype)

    public_url = f"/public/media/{entry.id}"
    short_url = f"/m/{entry.short_code}"

    return {
        "status": "uploaded",
        "media_id": entry.id,
        "filetype": filetype,
        "size_mb": size_mb,
        "public_url": public_url,
        "short_url": short_url
    }


@router.get("/all")
def list_media():
    db = SessionLocalSys()
    try:
        rows = db.query(MediaFile).order_by(MediaFile.uploaded_at.desc()).all()
        result = []
        for m in rows:
            result.append({
                "id": m.id,
                "filename": m.filename,
                "filetype": m.filetype,
                "size_mb": m.size_mb,
                "uploaded_at": m.uploaded_at,
                "public": m.public,
                "thumbnail": (m.thumbnail_path if m.thumbnail_path else None),
                "public_url": f"/public/media/{m.id}",
                "short_url": f"/m/{m.short_code}" if m.short_code else None
            })
        return result
    finally:
        db.close()

# Serve thumbnail
@router.get("/thumb/{media_id}")
def get_thumb(media_id: int):
    db = SessionLocalSys()
    try:
        m = db.query(MediaFile).get(media_id)
        if not m or not m.thumbnail_path:
            raise HTTPException(status_code=404, detail="Thumbnail not found")
        return FileResponse(m.thumbnail_path, media_type="image/jpeg", headers={"Cache-Control":"public,max-age=86400"})
    finally:
        db.close()

# Public access with optional password check via query param or header
@router.get("/public/{media_id}")
def public_access(media_id: int, password: str | None = None):
    db = SessionLocalSys()
    try:
        entry = db.query(MediaFile).get(media_id)
        if not entry:
            raise HTTPException(status_code=404, detail="File not found")
        # check public flag
        if not entry.public:
            # if password matches, allow
            from media_utils import verify_password
            if password and entry.password_hash and verify_password(password, entry.password_hash):
                pass
            else:
                raise HTTPException(status_code=401, detail="Protected media")
        # send with caching headers
        headers = {
            "Cache-Control": "public, max-age=604800",  # 7 days
        }
        return FileResponse(entry.filepath, headers=headers)
    finally:
        db.close()

# Short URL redirect
@router.get("/m/{code}")
def short_redirect(code: str):
    db = SessionLocalSys()
    try:
        entry = db.query(MediaFile).filter(MediaFile.short_code == code).first()
        if not entry:
            raise HTTPException(status_code=404, detail="Not found")
        return RedirectResponse(url=f"/public/media/{entry.id}")
    finally:
        db.close()

# Delete media (removes file + DB entry)
@router.delete("/{media_id}")
def delete_media(media_id: int):
    db = SessionLocalSys()
    try:
        entry = db.query(MediaFile).get(media_id)
        if not entry:
            raise HTTPException(status_code=404, detail="Not found")
        # delete files
        try:
            if entry.thumbnail_path and os.path.exists(entry.thumbnail_path):
                os.remove(entry.thumbnail_path)
            if entry.filepath and os.path.exists(entry.filepath):
                os.remove(entry.filepath)
        except Exception:
            pass
        db.delete(entry)
        db.commit()
        return {"status":"deleted", "id": media_id}
    finally:
        db.close()
