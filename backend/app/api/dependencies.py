from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import decode_token
from app.infrastructure.cloud.base import CloudStorageProvider
from app.infrastructure.cloud.local_provider import LocalLogProvider
from app.infrastructure.cloud.s3_provider import S3Provider
from app.infrastructure.database.database import get_db
from app.infrastructure.repositories.sqlalchemy_user_repository import SqlAlchemyUserRepository

auth_scheme = HTTPBearer(auto_error=False)


def get_user_repository(db: Session = Depends(get_db)) -> SqlAlchemyUserRepository:
    return SqlAlchemyUserRepository(db)


def get_cloud_provider() -> CloudStorageProvider:
    settings = get_settings()
    if settings.s3_bucket_name:
        return S3Provider()
    return LocalLogProvider()


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(auth_scheme),
) -> dict:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")

    try:
        payload = decode_token(credentials.credentials)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc

    return {
        "username": payload.get("sub", ""),
        "role": payload.get("role", "viewer"),
    }


def require_admin(user: dict = Depends(get_current_user)) -> dict:
    if user.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    return user
