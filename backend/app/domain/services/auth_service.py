from app.core.security import create_access_token, verify_password
from app.domain.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository

    def login(self, username: str, password: str) -> str | None:
        user = self._user_repository.get_by_username(username)
        if not user:
            return None

        if not verify_password(password, user.password_hash):
            return None

        return create_access_token(subject=user.username, role=user.role)
