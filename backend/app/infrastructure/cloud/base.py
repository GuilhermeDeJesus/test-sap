from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class CloudLogObject:
    name: str
    size: int


class CloudStorageProvider(Protocol):
    def list_logs(self) -> list[CloudLogObject]:
        ...

    def get_log_bytes(self, file_name: str) -> bytes:
        ...

    def generate_presigned_download_url(self, file_name: str, expires_seconds: int = 300) -> str:
        ...
