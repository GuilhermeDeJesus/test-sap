import boto3
from botocore.exceptions import ClientError

from app.core.config import get_settings
from app.infrastructure.cloud.base import CloudLogObject, CloudStorageProvider


class S3Provider(CloudStorageProvider):
    def __init__(self) -> None:
        settings = get_settings()
        self._bucket = settings.s3_bucket_name
        self._client = boto3.client(
            "s3",
            region_name=settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id or None,
            aws_secret_access_key=settings.aws_secret_access_key or None,
        )

    def list_logs(self) -> list[CloudLogObject]:
        response = self._client.list_objects_v2(Bucket=self._bucket)
        contents = response.get("Contents", [])
        return [CloudLogObject(name=obj["Key"], size=obj.get("Size", 0)) for obj in contents]

    def get_log_bytes(self, file_name: str) -> bytes:
        try:
            response = self._client.get_object(Bucket=self._bucket, Key=file_name)
        except ClientError as exc:
            raise FileNotFoundError(file_name) from exc
        return response["Body"].read()

    def generate_presigned_download_url(self, file_name: str, expires_seconds: int = 300) -> str:
        return self._client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self._bucket, "Key": file_name},
            ExpiresIn=expires_seconds,
        )
