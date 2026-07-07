from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.api.dependencies import get_user_repository
from app.core.rate_limit import login_rate_limiter
from app.domain.services.auth_service import AuthService
from app.schemas.auth import LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, request: Request, user_repository=Depends(get_user_repository)):
    client_ip = request.client.host if request.client else "unknown"
    if not login_rate_limiter.is_allowed(client_ip, max_requests=5, window_seconds=60):
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many login attempts")

    auth_service = AuthService(user_repository)
    token = auth_service.login(payload.username, payload.password)

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    return TokenResponse(access_token=token)
