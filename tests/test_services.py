from datetime import date

import pytest
from sqlalchemy import Date, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from sqlalchemy.pool import StaticPool

from server.services import CrudService


class WidgetBase(DeclarativeBase):
    pass


class Widget(WidgetBase):
    __tablename__ = "test_widget"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(40), nullable=False)
    created_on: Mapped[date] = mapped_column(Date, nullable=False)


class TeamMembership(WidgetBase):
    __tablename__ = "test_team_membership"

    player_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    team_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    points: Mapped[int] = mapped_column(Integer, nullable=False)


class MatchRecord(WidgetBase):
    __tablename__ = "test_match_record"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_team_one: Mapped[int] = mapped_column(Integer, nullable=False)
    id_team_two: Mapped[int] = mapped_column(Integer, nullable=False)
    id_team_winner: Mapped[int | None] = mapped_column(Integer)
    score_team_one: Mapped[int] = mapped_column(Integer, nullable=False)
    score_team_two: Mapped[int] = mapped_column(Integer, nullable=False)


class FakeUnitOfWork:
    def __init__(self, session):
        self.session = session

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            self.session.rollback()
        self.session.close()

    def commit(self):
        self.session.commit()


@pytest.fixture
def service():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    WidgetBase.metadata.create_all(engine)
    session_factory = sessionmaker(
        bind=engine, expire_on_commit=False, autoflush=False
    )
    return CrudService(
        lambda: FakeUnitOfWork(session_factory()),
        entity_models={
            "widgets": Widget,
            "team_memberships": TeamMembership,
            "matches": MatchRecord,
        },
    )


def test_service_create_list_read_update_and_delete(service):
    created = service.create_entity(
        "widgets", {"name": "Arena", "created_on": "2025-01-02"}
    )
    identifier = created["id"]

    assert created == {
        "id": identifier,
        "name": "Arena",
        "created_on": "2025-01-02",
    }
    assert service.list_entities("widgets") == [created]
    assert service.get_entity("widgets", identifier) == created
    assert service.update_entity(
        "widgets", identifier, {"name": "Final Arena"}
    )["name"] == "Final Arena"
    assert service.delete_entity("widgets", identifier) == {
        "deleted": True,
        "id": identifier,
    }
    assert service.list_entities("widgets") == []


@pytest.mark.parametrize(
    "values",
    [
        {"unknown": "field"},
        {"name": 7},
        {"created_on": "not-a-date"},
        {},
    ],
)
def test_service_rejects_invalid_create_data(service, values):
    with pytest.raises(ValueError):
        service.create_entity("widgets", values)


def test_service_rejects_primary_key_updates(service):
    created = service.create_entity(
        "widgets", {"name": "Arena", "created_on": "2025-01-02"}
    )

    with pytest.raises(ValueError, match="Primary key"):
        service.update_entity("widgets", created["id"], {"id": 9})


def test_service_rejects_unknown_entities(service):
    with pytest.raises(ValueError, match="Unknown entity"):
        service.list_entities("private_models")


def test_service_reports_missing_record(service):
    with pytest.raises(LookupError, match="not found"):
        service.get_entity("widgets", 999)


def test_service_accepts_composite_primary_keys(service):
    created = service.create_entity(
        "team_memberships",
        {"player_id": 12, "team_id": 8, "points": 4},
    )
    identifier = {"player_id": 12, "team_id": 8}

    assert service.get_entity("team_memberships", identifier) == created
    assert service.delete_entity("team_memberships", identifier)["deleted"]


@pytest.mark.parametrize(
    ("first_score", "second_score", "expected_winner"),
    [(2, 1, 10), (1, 2, 20), (3, 3, None)],
)
def test_updating_match_score_recalculates_winner(
    service, first_score, second_score, expected_winner
):
    match = service.create_entity(
        "matches",
        {
            "id_team_one": 10,
            "id_team_two": 20,
            "score_team_one": 0,
            "score_team_two": 0,
        },
    )

    updated = service.update_entity(
        "matches",
        match["id"],
        {
            "score_team_one": first_score,
            "score_team_two": second_score,
        },
    )

    assert updated["id_team_winner"] == expected_winner


def test_service_rejects_values_that_exceed_string_length(service):
    with pytest.raises(ValueError, match="40 characters"):
        service.create_entity(
            "widgets",
            {"name": "x" * 41, "created_on": "2025-01-02"},
        )
