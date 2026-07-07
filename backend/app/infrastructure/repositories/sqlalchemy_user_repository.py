from sqlalchemy.orm import Session

from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepository
from app.infrastructure.database.models import UserModel


class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, db: Session):
        self._db = db

    def get_by_username(self, username: str) -> User | None:
        model = self._db.query(UserModel).filter(UserModel.username == username).first()
        if not model:
            return None
        return User(
            id=model.id,
            username=model.username,
            password_hash=model.password_hash,
            role=model.role,
        )
