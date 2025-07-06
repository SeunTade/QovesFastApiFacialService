import hashlib
import base64

def get_image_hash(image_str: str):
    return hashlib.sha256(image_str.encode()).hexdigest()