from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response

from app.api.dependencies import get_cloud_provider, get_current_user, require_admin
from app.domain.services.log_service import LogService
from app.schemas.logs import LogFileResponse, PresignedResponse

router = APIRouter(prefix="/logs", tags=["logs"])


@router.get("", response_model=list[LogFileResponse])
def list_logs(user=Depends(get_current_user), provider=Depends(get_cloud_provider)):
    _ = user
    service = LogService(provider)
    logs = service.list_logs()
    return [LogFileResponse(name=log.name, size=log.size) for log in logs]


@router.get("/{file_name}")
def download_log(file_name: str, user=Depends(require_admin), provider=Depends(get_cloud_provider)):
    _ = user
    service = LogService(provider)
    try:
        content = service.download(file_name)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="File not found") from exc

    return Response(
        content=content,
        media_type="text/plain",
        headers={"Content-Disposition": f'attachment; filename="{file_name}"'},
    )


@router.post("/{file_name}/presigned", response_model=PresignedResponse)
def presigned_url(
    file_name: str,
    expires_seconds: int = Query(default=300, ge=60, le=3600),
    user=Depends(require_admin),
    provider=Depends(get_cloud_provider),
):
    _ = user
    service = LogService(provider)
    try:
        url = service.create_presigned(file_name, expires_seconds=expires_seconds)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="File not found") from exc
    return PresignedResponse(url=url)
