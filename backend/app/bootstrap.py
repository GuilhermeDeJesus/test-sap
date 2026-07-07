from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.infrastructure.database.models import UserModel


def seed_users(db: Session) -> None:
    if db.query(UserModel).count() > 0:
        return

    db.add_all(
        [
            UserModel(username="admin", password_hash=hash_password("123456"), role="admin"),
            UserModel(username="viewer", password_hash=hash_password("123456"), role="viewer"),
        ]
    )
    db.commit()
