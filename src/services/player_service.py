from datetime import datetime
from typing import Callable, TypedDict

from models import Player, PlayerProfile
from repositories import PlayerRepository
from repositories.unit_of_work import SqlAlchemyUnitOfWork
from services.errors import NotFoundError, ValidationError


PlayerValidationError = ValidationError
PlayerNotFoundError = NotFoundError


class PlayerListItem(TypedDict):
    id: int
    nickname: str
    region: str
    has_profile: bool


class PlayerService:
    def __init__(
        self,
        uow_factory: Callable[[], SqlAlchemyUnitOfWork],
    ) -> None:
        self.uow_factory = uow_factory

    def list_players(self) -> list[PlayerListItem]:
        with self.uow_factory() as uow:
            players = PlayerRepository(uow, Player).get_all()
            return [self._to_dto(player) for player in players]

    def search_players(self, nickname: str) -> list[PlayerListItem]:
        if not isinstance(nickname, str) or not nickname.strip():
            raise PlayerValidationError("nickname must be a non-empty string")

        with self.uow_factory() as uow:
            players = PlayerRepository(uow, Player).search_by_nickname(
                nickname.strip()
            )
            return [self._to_dto(player) for player in players]

    def get_player(self, player_id: int) -> PlayerListItem:
        self._validate_id(player_id)
        with self.uow_factory() as uow:
            player = PlayerRepository(uow, Player).get(player_id)
            if player is None:
                raise PlayerNotFoundError("Player not found")
            return self._to_dto(player)

    def create_player(
        self,
        nickname: str,
        email: str,
        region_id: int,
        ranking_position: int | None = None,
    ) -> PlayerListItem:
        self._validate_text(nickname, "nickname")
        self._validate_text(email, "email")
        self._validate_id(region_id, "region_id")
        if ranking_position is not None and (
            isinstance(ranking_position, bool)
            or not isinstance(ranking_position, int)
            or ranking_position < 0
        ):
            raise PlayerValidationError(
                "ranking_position must be a non-negative integer"
            )

        now = datetime.now()
        player = Player(
            nickname=nickname.strip(),
            email=email.strip(),
            birth_date=now,
            registration_date=now,
            id_region=region_id,
            active=True,
        )
        if ranking_position is not None:
            player.profile = PlayerProfile(ranking_position=ranking_position)

        with self.uow_factory() as uow:
            repo = PlayerRepository(uow, Player)
            repo.add(player)
            uow.session.flush()
            return self._to_dto(player)

    def update_player(self, player_id: int, nickname: str) -> PlayerListItem:
        self._validate_id(player_id)
        self._validate_text(nickname, "nickname")
        with self.uow_factory() as uow:
            repo = PlayerRepository(uow, Player)
            player = repo.get(player_id)
            if player is None:
                raise PlayerNotFoundError("Player not found")
            player.nickname = nickname.strip()
            uow.session.flush()
            return self._to_dto(player)

    def delete_player(self, player_id: int) -> dict[str, bool]:
        self._validate_id(player_id)
        with self.uow_factory() as uow:
            repo = PlayerRepository(uow, Player)
            player = repo.get(player_id)
            if player is None:
                raise PlayerNotFoundError("Player not found")
            if player.profile is not None:
                uow.session.delete(player.profile)
            repo.delete(player)
            uow.session.flush()
            return {"deleted": True}

    @staticmethod
    def _to_dto(player: Player) -> PlayerListItem:
        return {
            "id": player.id,
            "nickname": player.nickname,
            "region": getattr(player.region, "name", None)
            or str(getattr(player, "id_region", "-")),
            "has_profile": bool(getattr(player, "profile", None)),
        }

    @staticmethod
    def _validate_id(value: int, field: str = "id") -> None:
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise PlayerValidationError(f"{field} must be a positive integer")

    @staticmethod
    def _validate_text(value: str, field: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise PlayerValidationError(f"{field} must be a non-empty string")
