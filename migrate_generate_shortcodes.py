# server/migrate_generate_shortcodes.py

from system_database import SessionLocalSys
from media_models import MediaFile
from media_utils import base62_encode

def main():
    db = SessionLocalSys()

    try:
        # Ambil semua row yang belum punya short_code
        rows = db.query(MediaFile).filter(MediaFile.short_code == None).all()

        print(f"Found {len(rows)} rows without short_code")

        for row in rows:
            # encode id menjadi base62
            sc = base62_encode(row.id)
            row.short_code = sc
            print(f"ID {row.id} -> short_code = {sc}")

        db.commit()
        print("Short code generation complete!")

    finally:
        db.close()


if __name__ == "__main__":
    main()
