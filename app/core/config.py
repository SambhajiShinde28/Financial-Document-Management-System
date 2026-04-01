from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    app_name: str = "Financial Document Management API"
    app_version: str = "1.0.0"
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    database_url: str = f"sqlite:///{BASE_DIR / 'financial_documents.db'}"
    upload_dir: Path = BASE_DIR / "app" / "storage" / "documents"
    vector_db_dir: Path = BASE_DIR / "app" / "storage" / "vector_db"
    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    chunk_size: int = 700
    chunk_overlap: int = 120

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
