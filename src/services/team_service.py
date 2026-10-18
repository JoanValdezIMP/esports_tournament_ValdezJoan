from datetime import date
from typing import Callable, TypedDict

from models import Player, PlayerTeam, Region, Team
from repositories import TeamRepository
from repositories.unit_of_work import SqlAlchemyUnitOfWork
from services.errors import NotFoundError, ValidationError


TeamValidationError = ValidationError
TeamNotFoundError = NotFoundError


class TeamItem(TypedDict):
    id: int
    name: str
    region: str


class TeamService:
    def __init__(
        self,
        uow_factory: Callable[[], SqlAlchemyUnitOfWork],
    ) -> None:
        self.uow_factory = uow_factory

    def list_teams(self) -> list[TeamItem]:
        with self.uow_factory() as uow:
            teams = TeamRepository(uow, Team).get_all()
            return [self._to_dto(team) for team in teams]

    def get_team(self, team_id: int) -> TeamItem:
        self._validate_id(team_id, "id")
        with self.uow_factory() as uow:
            team = TeamRepository(uow, Team).get(team_id)
            if team is None:
                raise TeamNotFoundError("Team not found")
            return self._to_dto(team)

    def create_team(self, name: str, region_id: int) -> TeamItem:
        self._validate_text(name, "name")
        self._validate_id(region_id, "region_id")

        with self.uow_factory() as uow:
            region = uow.session.get(Region, region_id)
            if region is None:
                raise TeamNotFoundError("Region not found")
            team = Team(
                name=name.strip(),
                id_region=region_id,
                creation_date=date.today(),
                active=True,
            )
            repo = TeamRepository(uow, Team)
            repo.add(team)
            uow.session.flush()
            return self._to_dto(team)

    def update_team(self, team_id: int, name: str) -> TeamItem:
        self._validate_id(team_id, "id")
        self._validate_text(name, "name")
        with self.uow_factory() as uow:
            repo = TeamRepository(uow, Team)
            team = repo.get(team_id)
            if team is None:
                raise TeamNotFoundError("Team not found")
            team.name = name.strip()
            uow.session.flush()
            return self._to_dto(team)

    def delete_team(self, team_id: int) -> dict[str, bool]:
        self._validate_id(team_id, "id")
        with self.uow_factory() as uow:
            repo = TeamRepository(uow, Team)
            team = repo.get(team_id)
            if team is None:
                raise TeamNotFoundError("Team not found")
            if team.team_players or team.team_tournaments:
                raise TeamValidationError(
                    "Team cannot be deleted while it has associated players "
                    "or tournaments"
                )
            repo.delete(team)
            uow.session.flush()
            return {"deleted": True}

    def assign_player(
        self,
        team_id: int,
        player_id: int,
        points_obtained: int,
    ) -> dict[str, bool]:
        self._validate_id(team_id, "team_id")
        self._validate_id(player_id, "player_id")
        if (
            isinstance(points_obtained, bool)
            or not isinstance(points_obtained, int)
            or points_obtained < 0
        ):
            raise TeamValidationError(
                "points_obtained must be a non-negative integer"
            )

        with self.uow_factory() as uow:
            if uow.session.get(Team, team_id) is None:
                raise TeamNotFoundError("Team not found")
            if uow.session.get(Player, player_id) is None:
                raise TeamNotFoundError("Player not found")
            association_key = (player_id, team_id)
            if uow.session.get(PlayerTeam, association_key) is not None:
                raise TeamValidationError(
                    "Player is already assigned to this team"
                )
            uow.session.add(
                PlayerTeam(
                    id_player=player_id,
                    id_team=team_id,
                    points_obtained=points_obtained,
                )
            )
            uow.session.flush()
            return {"assigned": True}

    @staticmethod
    def _to_dto(team: Team) -> TeamItem:
        return {
            "id": team.id,
            "name": team.name,
            "region": getattr(team.region, "name", None)
            or str(getattr(team, "id_region", "-")),
        }

    @staticmethod
    def _validate_id(value: int, field: str) -> None:
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise TeamValidationError(f"{field} must be a positive integer")

    @staticmethod
    def _validate_text(value: str, field: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise TeamValidationError(f"{field} must be a non-empty string")
