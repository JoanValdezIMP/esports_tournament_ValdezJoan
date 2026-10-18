from datetime import datetime
from typing import Callable, TypedDict

from models import Match, Team, Tournament
from repositories import MatchRepository
from repositories.unit_of_work import SqlAlchemyUnitOfWork
from services.errors import NotFoundError, ValidationError


class MatchItem(TypedDict):
    id: int
    match_date: str
    tournament_id: int
    team_one_id: int
    team_two_id: int
    winner_id: int | None
    score_team_one: int
    score_team_two: int
    round_number: int
    duration_minutes: int


class MatchService:
    def __init__(
        self,
        uow_factory: Callable[[], SqlAlchemyUnitOfWork],
    ) -> None:
        self.uow_factory = uow_factory

    def list_matches(self) -> list[MatchItem]:
        with self.uow_factory() as uow:
            matches = MatchRepository(uow, Match).get_all()
            return [self._to_dto(match) for match in matches]

    def create_match(
        self,
        tournament_id: int,
        team_one_id: int,
        team_two_id: int,
        round_number: int,
        duration_minutes: int,
    ) -> MatchItem:
        self._validate_id(tournament_id, "tournament_id")
        self._validate_id(team_one_id, "team_one_id")
        self._validate_id(team_two_id, "team_two_id")
        if team_one_id == team_two_id:
            raise ValidationError("A match must have two different teams")
        self._validate_positive_integer(round_number, "round_number")
        self._validate_positive_integer(duration_minutes, "duration_minutes")

        with self.uow_factory() as uow:
            if uow.session.get(Tournament, tournament_id) is None:
                raise NotFoundError("Tournament not found")
            if uow.session.get(Team, team_one_id) is None:
                raise NotFoundError("First team not found")
            if uow.session.get(Team, team_two_id) is None:
                raise NotFoundError("Second team not found")

            match = Match(
                match_date=datetime.now(),
                score_team_one=0,
                score_team_two=0,
                round_number=round_number,
                duration_minutes=duration_minutes,
                id_tournament=tournament_id,
                id_team_one=team_one_id,
                id_team_two=team_two_id,
                id_team_winner=None,
            )
            MatchRepository(uow, Match).add(match)
            uow.session.flush()
            return self._to_dto(match)

    def update_result(
        self,
        match_id: int,
        score_team_one: int,
        score_team_two: int,
    ) -> MatchItem:
        self._validate_id(match_id, "id")
        self._validate_non_negative_integer(score_team_one, "score_team_one")
        self._validate_non_negative_integer(score_team_two, "score_team_two")
        with self.uow_factory() as uow:
            repo = MatchRepository(uow, Match)
            match = repo.get(match_id)
            if match is None:
                raise NotFoundError("Match not found")
            match.score_team_one = score_team_one
            match.score_team_two = score_team_two
            if score_team_one > score_team_two:
                match.id_team_winner = match.id_team_one
            elif score_team_two > score_team_one:
                match.id_team_winner = match.id_team_two
            else:
                match.id_team_winner = None
            uow.session.flush()
            return self._to_dto(match)

    def delete_match(self, match_id: int) -> dict[str, bool]:
        self._validate_id(match_id, "id")
        with self.uow_factory() as uow:
            repo = MatchRepository(uow, Match)
            match = repo.get(match_id)
            if match is None:
                raise NotFoundError("Match not found")
            repo.delete(match)
            uow.session.flush()
            return {"deleted": True}

    @staticmethod
    def _to_dto(match: Match) -> MatchItem:
        return {
            "id": match.id,
            "match_date": match.match_date.isoformat(timespec="minutes"),
            "tournament_id": match.id_tournament,
            "team_one_id": match.id_team_one,
            "team_two_id": match.id_team_two,
            "winner_id": match.id_team_winner,
            "score_team_one": match.score_team_one,
            "score_team_two": match.score_team_two,
            "round_number": match.round_number,
            "duration_minutes": match.duration_minutes,
        }

    @staticmethod
    def _validate_id(value: int, field: str) -> None:
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValidationError(f"{field} must be a positive integer")

    @staticmethod
    def _validate_positive_integer(value: int, field: str) -> None:
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValidationError(f"{field} must be a positive integer")

    @staticmethod
    def _validate_non_negative_integer(value: int, field: str) -> None:
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValidationError(f"{field} must be a non-negative integer")
