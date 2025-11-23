import cloudinary
import cloudinary.uploader
from conf.config import settings
from typing import BinaryIO


cloudinary.config(
    cloud_name=settings.cloudinary_name,
    api_key=settings.cloudinary_api_key,
    api_secret=settings.cloudinary_api_secret,
    secure=True,
)


def upload_avatar(file_stream: BinaryIO, public_id: str, overwrite: bool = True):
    r = cloudinary.uploader.upload(
        file_stream,
        public_id=public_id,
        folder="rest_api_avatars",
        overwrite=overwrite,
    )

    return r["secure_url"]
