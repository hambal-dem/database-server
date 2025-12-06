# migrate_generate_thumbs.py

import os
from system_database import SessionLocalSys
from media_models import MediaFile
from media_utils import create_image_thumbnail, create_video_thumbnail

THUMB_DIR = os.path.join("media_storage", "thumbs")
os.makedirs(THUMB_DIR, exist_ok=True)

def generate_thumbnail(row: MediaFile):
    src = row.filepath

    if not os.path.exists(src):
        print(f"[SKIP] File not found: {src}")
        return None

    # Nama thumbnail = thumb_10.jpg (menggunakan ID)
    dest = os.path.join(THUMB_DIR, f"thumb_{row.id}.jpg")

    # Buat thumbnail sesuai tipe
    if row.filetype == "image":
        ok = create_image_thumbnail(src, dest)
        if ok:
            return dest

    elif row.filetype == "video":
        ok = create_video_thumbnail(src, dest)
        if ok:
            return dest

    return None


def main():
    db = SessionLocalSys()

    # Ambil baris yang belum punya thumbnail
    rows = db.query(MediaFile).filter(MediaFile.thumbnail_path == None).all()
    print(f"Total media without thumbnail: {len(rows)}")

    for r in rows:
        print(f"Processing ID={r.id} ({r.filename})")
        thumb = generate_thumbnail(r)

        if thumb:
            r.thumbnail_path = thumb
            db.commit()
            print(f"  ✓ Thumbnail generated: {thumb}")
        else:
            print("  ✗ Failed to generate thumbnail")

    print("Thumbnail generation complete!")
    db.close()


if __name__ == "__main__":
    main()
