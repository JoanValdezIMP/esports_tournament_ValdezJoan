from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Callable, TypedDict

from models import (
    Region,
    Team,
    TeamTournament,
    Tournament,
    TournamentMode,
    TournamentStatus,
    VideoGameType,
)
from repositories import TournamentRepository
from repositories.unit_of_work import SqlAlchemyUnitOfWork
from services.errors import NotFoundError, ValidationError


class TournamentItem(TypedDict):
    id: int
    name: str
    start_date: str
    end_date: str | None
    prize_pool: float
    max_teams: int
    region_id: int
    video_game_type_id: int
    tournament_mode_id: int
    tournament_status_id: int
    region: str
    video_game_type: str
    tournament_mode: str
    tournament_status: str


class TournamentService:
    def __init__(
        self,
        uow_factory: Callable[[], SqlAlchemyUnitOfWork],
    ) -> None:
        self.uow_factory = uow_factory

    def list_tournaments(self) -> list[TournamentItem]:
        with self.uow_factory() as uow:
            tournaments = TournamentRepository(uow, Tournament).get_all()
            return [self._to_dto(tournament) for tournament in tournaments]

    def get_tournament(self, tournament_id: int) -> TournamentItem:
        self._validate_id(tournament_id, "id")
        with self.uow_factory() as uow:
            tournament = TournamentRepository(uow, Tournament).get(
                tournament_id
            )
            if tournament is None:
                raise NotFoundError("Tournament not found")
            return self._to_dto(tournament)

    def create_tournament(
        self,
        name: str,
        start_date: str,
        end_date: str | None,
        prize_pool: int | float | str,
        max_teams: int,
        region_id: int,
        video_game_type_id: int,
        tournament_mode_id: int,
        tournament_status_id: int,
    ) -> TournamentItem:
        self._validate_name(name)
        parsed_start = self._parse_date(start_date, "start_date")
        parsed_end = (
            self._parse_date(end_date, "end_date")
            if end_date is not None
            else None
        )
        if parsed_end is not None and parsed_end < parsed_start:
            raise ValidationError("end_date cannot be before start_date")
        prize = self._parse_prize_pool(prize_pool)
        self._validate_positive_integer(max_teams, "max_teams")
        self._validate_id(region_id, "region_id")
        self._validate_id(video_game_type_id, "video_game_type_id")
        self._validate_id(tournament_mode_id, "tournament_mode_id")
        self._validate_id(tournament_status_id, "tournament_status_id")

        with self.uow_factory() as uow:
            references = (
                (Region, region_id, "Region"),
                (VideoGameType, video_game_type_id, "Video game type"),
                (TournamentMode, tournament_mode_id, "Tournament mode"),
                (TournamentStatus, tournament_status_id, "Tournament status"),
            )
            for model, item_id, label in references:
                if uow.session.get(model, item_id) is None:
                    raise NotFoundError(f"{label} not found")
            tournament = Tournament(
                name=name.strip(),
                start_date=parsed_start,
                end_date=parsed_end,
                prize_pool=prize,
                max_teams=max_teams,
                id_region=region_id,
                id_video_game_type=video_game_type_id,
                id_tournament_mode=tournament_mode_id,
                id_tournament_status=tournament_status_id,
            )
            TournamentRepository(uow, Tournament).add(tournament)
            uow.session.flush()
            return self._to_dto(tournament)

    def update_tournament(
        self,
        tournament_id: int,
        name: str,
        start_date: str,
        end_date: str | None,
        prize_pool: int | float | str,
        max_teams: int,
    ) -> TournamentItem:
        self._validate_id(tournament_id, "id")
        self._validate_name(name)
        parsed_start = self._parse_date(start_date, "start_date")
        parsed_end = (
            self._parse_date(end_date, "end_date")
            if end_date is not None
            else None
        )
        if parsed_end is not None and parsed_end < parsed_start:
            raise ValidationError("end_date cannot be before start_date")
        prize = self._parse_prize_pool(prize_pool)
        self._validate_positive_integer(max_teams, "max_teams")
        with self.uow_factory() as uow:
            tournament = TournamentRepository(uow, Tournament).get(
                tournament_id
            )
            if tournament is None:
                raise NotFoundError("Tournament not found")
            if max_teams < len(tournament.tournament_teams):
                raise ValidationError(
                    "max_teams cannot be below registered teams"
                )
            tournament.name = name.strip()
            tournament.start_date = parsed_start
            tournament.end_date = parsed_end
            tournament.prize_pool = prize
            tournament.max_teams = max_teams
            uow.session.flush()
            return self._to_dto(tournament)

    def delete_tournament(self, tournament_id: int) -> dict[str, bool]:
        self._validate_id(tournament_id, "id")
        with self.uow_factory() as uow:
            repo = TournamentRepository(uow, Tournament)
            tournament = repo.get(tournament_id)
            if tournament is None:
                raise NotFoundError("Tournament not found")
            if tournament.matches or tournament.tournament_teams:
                raise ValidationError(
                    "Tournament cannot be deleted while it has matches "
                    "or registered teams"
                )
            repo.delete(tournament)
            uow.session.flush()
            return {"deleted": True}

    def register_team(
        self,
        tournament_id: int,
        team_id: int,
    ) -> dict[str, bool]:
        self._validate_id(tournament_id, "tournament_id")
        self._validate_id(team_id, "team_id")
        with self.uow_factory() as uow:
            tournament = uow.session.get(Tournament, tournament_id)
            if tournament is None:
                raise NotFoundError("Tournament not found")
            if uow.session.get(Team, team_id) is None:
                raise NotFoundError("Team not found")
            association_key = (team_id, tournament_id)
            if uow.session.get(TeamTournament, association_key) is not None:
                raise ValidationError(
                    "Team is already registered in this tournament"
                )
            if len(tournament.tournament_teams) >= tournament.max_teams:
                raise ValidationError("Tournament has reached its team limit")
            uow.session.add(
                TeamTournament(id_team=team_id, id_tournament=tournament_id)
            )
            uow.session.flush()
            return {"registered": True}

    @staticmethod
    def _to_dto(tournament: Tournament) -> TournamentItem:
        return {
            "id": tournament.id,
            "name": tournament.name,
            "start_date": tournament.start_date.isoformat(),
            "end_date": (
                tournament.end_date.isoformat()
                if tournament.end_date
                else None
            ),
            "prize_pool": float(tournament.prize_pool or 0),
            "max_teams": tournament.max_teams,
            "region_id": tournament.id_region,
            "video_game_type_id": tournament.id_video_game_type,
            "tournament_mode_id": tournament.id_tournament_mode,
            "tournament_status_id": tournament.id_tournament_status,
            "region": tournament.region.name,
            "video_game_type": tournament.video_game_type.name,
            "tournament_mode": tournament.tournament_mode.name,
            "tournament_status": tournament.tournament_status.name,
        }

    @staticmethod
    def _parse_date(value: str, field: str) -> date:
        if not isinstance(value, str):
            raise ValidationError(f"{field} must use YYYY-MM-DD format")
        try:
            return date.fromisoformat(value)
        except ValueError as error:
            raise ValidationError(
                f"{field} must use YYYY-MM-DD format"
            ) from error

    @staticmethod
    def _parse_prize_pool(value: int | float | str) -> Decimal:
        if isinstance(value, bool) or not isinstance(value, (int, float, str)):
            raise ValidationError("prize_pool must be a non-negative number")
        try:
            amount = Decimal(str(value))
        except InvalidOperation as error:
            raise ValidationError(
                "prize_pool must be a non-negative number"
            ) from error
        if (
            not amount.is_finite()
            or amount < 0
            or amount.as_tuple().exponent < -2
        ):
            raise ValidationError(
                "prize_pool must be non-negative and have at most "
                "two decimal places"
            )
        return amount

    @staticmethod
    def _validate_name(name: str) -> None:
        if not isinstance(name, str) or not name.strip():
            raise ValidationError("name must be a non-empty string")
        if len(name.strip()) > 150:
            raise ValidationError("name must be at most 150 characters")

    @staticmethod
    def _validate_id(value: int, field: str) -> None:
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValidationError(f"{field} must be a positive integer")

    @staticmethod
    def _validate_positive_integer(value: int, field: str) -> None:
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValidationError(f"{field} must be a positive integer")
