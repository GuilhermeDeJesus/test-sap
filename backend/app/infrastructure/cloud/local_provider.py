from pathlib import Path

from app.core.config import get_settings
from app.core.security import create_temporary_download_token
from app.infrastructure.cloud.base import CloudLogObject, CloudStorageProvider


class LocalLogProvider(CloudStorageProvider):
    def __init__(self) -> None:
        settings = get_settings()
        self._base_path = Path(settings.local_logs_path)
        self._base_path.mkdir(parents=True, exist_ok=True)

    def list_logs(self) -> list[CloudLogObject]:
        return [
            CloudLogObject(name=path.name, size=path.stat().st_size)
            for path in sorted(self._base_path.glob("*.log"))
        ]

    def get_log_bytes(self, file_name: str) -> bytes:
        target = self._base_path / file_name
        if not target.exists() or not target.is_file():
            raise FileNotFoundError(file_name)
        return target.read_bytes()

    def generate_presigned_download_url(self, file_name: str, expires_seconds: int = 300) -> str:
        token = create_temporary_download_token(file_name=file_name, expires_seconds=expires_seconds)
        return f"/logs/public-download?token={token}"
