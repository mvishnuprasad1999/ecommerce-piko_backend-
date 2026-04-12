import cloudinary
import cloudinary.uploader
import os
from dotenv import load_dotenv
load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_NAME"),
    api_key=os.getenv("CLOUDINARY_APIKEY"),
    api_secret=os.getenv("CLOUDINARY_API_KEY_SECRET")    
)

def upload_image(file=None, path: str = None):
    if file:
        # For FastAPI UploadFile
        result = cloudinary.uploader.upload(file.file)
    elif path:
        # For local file path
        result = cloudinary.uploader.upload(path)
    else:
        raise ValueError("Provide either file or path")

    return {
        "url": result["secure_url"],
        "public_id": result["public_id"]
    }