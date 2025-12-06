# server/media_utils.py
import os
import hashlib
import base64
import random
import string
import subprocess
from PIL import Image

# Simple base62 encoder for short codes
ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
def base62_encode(num: int) -> str:
    if num == 0:
        return ALPHABET[0]
    arr = []
    base = len(ALPHABET)
    while num:
        rem = num % base
        num = num // base
        arr.append(ALPHABET[rem])
    arr.reverse()
    return ''.join(arr)

# simple password hash using pbkdf2_hmac
import hashlib, os
def hash_password(password: str, salt: bytes = None) -> str:
    if salt is None:
        salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    return salt.hex() + ":" + dk.hex()

def verify_password(password: str, stored: str) -> bool:
    if not stored:
        return False
    salt_hex, dk_hex = stored.split(":")
    salt = bytes.fromhex(salt_hex)
    test = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    return test.hex() == dk_hex

# create image thumbnail via Pillow
def create_image_thumbnail(src_path: str, dst_path: str, size=(320, 180)):
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    with Image.open(src_path) as im:
        im.thumbnail(size)
        im.save(dst_path, format="JPEG", quality=85)
    return dst_path

# create video thumbnail via ffmpeg (first frame)
def create_video_thumbnail(src_path: str, dst_path: str, time_offset="00:00:01", size="320x180"):
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    # ffmpeg -ss 00:00:01 -i input.mp4 -frames:v 1 -s 320x180 -y output.jpg
    cmd = [
        "ffmpeg", "-ss", time_offset, "-i", src_path,
        "-frames:v", "1", "-s", size, "-y", dst_path
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return dst_path
    except Exception:
        return None
