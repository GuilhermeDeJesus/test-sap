from app.infrastructure.cloud.base import CloudLogObject, CloudStorageProvider


class LogService:
    def __init__(self, provider: CloudStorageProvider):
        self._provider = provider

    def list_logs(self) -> list[CloudLogObject]:
        return self._provider.list_logs()

    def download(self, file_name: str) -> bytes:
        return self._provider.get_log_bytes(file_name)

    def create_presigned(self, file_name: str, expires_seconds: int = 300) -> str:
        return self._provider.generate_presigned_download_url(file_name, expires_seconds)
