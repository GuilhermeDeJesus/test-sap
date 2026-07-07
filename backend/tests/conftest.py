from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.dependencies import get_cloud_provider, get_db
from app.bootstrap import seed_users
from app.infrastructure.database.database import Base
from app.infrastructure.cloud.local_provider import LocalLogProvider
from app.main import app


@pytest.fixture()
def client(tmp_path: Path):
    db_file = tmp_path / "test.db"
    engine = create_engine(f"sqlite:///{db_file}", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    seed_users(db)
    db.close()

    logs_dir = tmp_path / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    (logs_dir / "access.log").write_text("access line\n", encoding="utf-8")
    (logs_dir / "server.log").write_text("server line\n", encoding="utf-8")

    def override_get_db():
        testing_db = TestingSessionLocal()
        try:
            yield testing_db
        finally:
            testing_db.close()

    def override_get_cloud_provider():
        provider = LocalLogProvider()
        provider._base_path = logs_dir
        return provider

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_cloud_provider] = override_get_cloud_provider

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
