from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import settings


class FileService:
    @staticmethod
    def save_upload(file: UploadFile) -> Path:
        settings.upload_dir.mkdir(parents=True, exist_ok=True)
        extension = Path(file.filename or "").suffix.lower()
        stored_name = f"{uuid4().hex}{extension}"
        target_path = settings.upload_dir / stored_name

        with target_path.open("wb") as output_file:
            output_file.write(file.file.read())

        return target_path
