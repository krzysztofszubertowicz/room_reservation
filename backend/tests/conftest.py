from datetime import date, timedelta

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import models
from auth import get_password_hash
from database import get_db
from dependencies import get_current_user
from models import Equipment, Room, RoomType, User
from routers import reservation, rooms, users


@pytest.fixture(scope="session")
def engine():
    # Local, isolated database used only by the test suite.
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    return test_engine


@pytest.fixture(scope="function")
def db_session(engine):
    # Recreate schema for every test so each case starts clean.
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def app(db_session):
    app_instance = FastAPI()
    app_instance.include_router(users.router)
    app_instance.include_router(rooms.router)
    app_instance.include_router(reservation.router)

    app_instance.dependency_overrides[get_db] = lambda: db_session
    return app_instance


@pytest.fixture(scope="function")
def client(app):
    return TestClient(app)


@pytest.fixture(scope="function")
def seeded_entities(db_session):
    # Minimal dataset shared by login, room and reservation tests.
    admin_user = User(
        first_name="Admin",
        last_name="User",
        email="admin@example.com",
        password=get_password_hash("admin-pass"),
        role="admin",
    )
    regular_user = User(
        first_name="Regular",
        last_name="User",
        email="user@example.com",
        password=get_password_hash("user-pass"),
        role="uzytkownik",
    )

    lecture_type = RoomType(name="Lecture", description="Lecture room")
    projector = Equipment(name="Projector", description="Ceiling projector")
    whiteboard = Equipment(name="Whiteboard", description="Wall board")

    db_session.add_all([admin_user, regular_user, lecture_type, projector, whiteboard])
    db_session.commit()

    db_session.refresh(admin_user)
    db_session.refresh(regular_user)
    db_session.refresh(lecture_type)
    db_session.refresh(projector)
    db_session.refresh(whiteboard)

    room_a = Room(
        name="A-101",
        building="A",
        floor=1,
        seat_count=30,
        description="Primary lecture room",
        type_id=lecture_type.id,
    )
    room_a.equipment = [projector]

    db_session.add(room_a)
    db_session.commit()
    db_session.refresh(room_a)

    return {
        "admin_user": admin_user,
        "regular_user": regular_user,
        "lecture_type": lecture_type,
        "projector": projector,
        "whiteboard": whiteboard,
        "room_a": room_a,
        "future_date": date.today() + timedelta(days=1),
    }


@pytest.fixture(scope="function")
def auth_as_admin(app, seeded_entities):
    # Bypass auth for endpoints that need an admin user.
    app.dependency_overrides[get_current_user] = lambda: seeded_entities["admin_user"]
    try:
        yield
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture(scope="function")
def auth_as_regular_user(app, seeded_entities):
    # Same idea, but for a regular account.
    app.dependency_overrides[get_current_user] = lambda: seeded_entities["regular_user"]
    try:
        yield
    finally:
        app.dependency_overrides.pop(get_current_user, None)
