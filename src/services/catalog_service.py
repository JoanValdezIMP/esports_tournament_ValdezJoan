from typing import Callable, TypedDict

from models import (
    PlayerProfile,
    Region,
    TournamentMode,
    TournamentStatus,
    VideoGameType,
)
from repositories import (
    PlayerProfileRepository,
    RegionRepository,
    TournamentModeRepository,
    TournamentStatusRepository,
    VideoGameTypeRepository,
)
from repositories.unit_of_work import SqlAlchemyUnitOfWork
from services.errors import NotFoundError, ValidationError


class RegionItem(TypedDict):
    id: int
    name: str
    country_code: str


class NamedCatalogItem(TypedDict):
    id: int
    name: str
    description: str | None


class PlayerProfileItem(TypedDict):
    nickname: str
    ranking_position: int | None
    total_matches: int
    total_points: int


class CatalogService:
    def __init__(
        self,
        uow_factory: Callable[[], SqlAlchemyUnitOfWork],
    ) -> None:
        self.uow_factory = uow_factory

    def list_regions(self) -> list[RegionItem]:
        with self.uow_factory() as uow:
            regions = RegionRepository(uow, Region).get_all()
            return [
                {
                    "id": region.id,
                    "name": region.name,
                    "country_code": region.country_code,
                }
                for region in regions
            ]

    def create_region(self, name: str, country_code: str) -> RegionItem:
        self._validate_text(name, "name")
        self._validate_text(country_code, "country_code")
        if len(name.strip()) > 100:
            raise ValidationError("name must be at most 100 characters")
        if len(country_code.strip()) > 10:
            raise ValidationError("country_code must be at most 10 characters")

        with self.uow_factory() as uow:
            region = Region(
                name=name.strip(), country_code=country_code.strip()
            )
            RegionRepository(uow, Region).add(region)
            uow.session.flush()
            return {
                "id": region.id,
                "name": region.name,
                "country_code": region.country_code,
            }

    def list_tournament_statuses(self) -> list[NamedCatalogItem]:
        with self.uow_factory() as uow:
            statuses = TournamentStatusRepository(
                uow, TournamentStatus
            ).get_all()
            return [self._named_dto(status) for status in statuses]

    def create_tournament_status(
        self, name: str, description: str | None
    ) -> NamedCatalogItem:
        self._validate_name_description(name, description)
        with self.uow_factory() as uow:
            status = TournamentStatus(
                name=name.strip(),
                description=self._clean_description(description),
            )
            TournamentStatusRepository(uow, TournamentStatus).add(status)
            uow.session.flush()
            return self._named_dto(status)

    def list_tournament_modes(self) -> list[NamedCatalogItem]:
        with self.uow_factory() as uow:
            modes = TournamentModeRepository(uow, TournamentMode).get_all()
            return [self._named_dto(mode) for mode in modes]

    def create_tournament_mode(
        self,
        name: str,
        description: str | None,
    ) -> NamedCatalogItem:
        self._validate_name_description(name, description)
        with self.uow_factory() as uow:
            mode = TournamentMode(
                name=name.strip(),
                description=self._clean_description(description),
            )
            TournamentModeRepository(uow, TournamentMode).add(mode)
            uow.session.flush()
            return self._named_dto(mode)

    def update_tournament_mode(
        self,
        mode_id: int,
        name: str,
        description: str | None,
    ) -> NamedCatalogItem:
        self._validate_id(mode_id, "id")
        self._validate_name_description(name, description)
        with self.uow_factory() as uow:
            repo = TournamentModeRepository(uow, TournamentMode)
            mode = repo.get(mode_id)
            if mode is None:
                raise NotFoundError("Tournament mode not found")
            mode.name = name.strip()
            mode.description = self._clean_description(description)
            uow.session.flush()
            return self._named_dto(mode)

    def delete_tournament_mode(self, mode_id: int) -> dict[str, bool]:
        self._validate_id(mode_id, "id")
        with self.uow_factory() as uow:
            repo = TournamentModeRepository(uow, TournamentMode)
            mode = repo.get(mode_id)
            if mode is None:
                raise NotFoundError("Tournament mode not found")
            if mode.tournaments:
                raise ValidationError("Tournament mode is in use")
            repo.delete(mode)
            uow.session.flush()
            return {"deleted": True}

    def list_video_game_types(self) -> list[NamedCatalogItem]:
        with self.uow_factory() as uow:
            game_types = VideoGameTypeRepository(uow, VideoGameType).get_all()
            return [self._named_dto(game_type) for game_type in game_types]

    def create_video_game_type(
        self,
        name: str,
        description: str | None,
    ) -> NamedCatalogItem:
        self._validate_name_description(name, description)
        with self.uow_factory() as uow:
            game_type = VideoGameType(
                name=name.strip(),
                description=self._clean_description(description),
            )
            VideoGameTypeRepository(uow, VideoGameType).add(game_type)
            uow.session.flush()
            return self._named_dto(game_type)

    def update_video_game_type(
        self,
        game_type_id: int,
        name: str,
        description: str | None,
    ) -> NamedCatalogItem:
        self._validate_id(game_type_id, "id")
        self._validate_name_description(name, description)
        with self.uow_factory() as uow:
            repo = VideoGameTypeRepository(uow, VideoGameType)
            game_type = repo.get(game_type_id)
            if game_type is None:
                raise NotFoundError("Video game type not found")
            game_type.name = name.strip()
            game_type.description = self._clean_description(description)
            uow.session.flush()
            return self._named_dto(game_type)

    def delete_video_game_type(self, game_type_id: int) -> dict[str, bool]:
        self._validate_id(game_type_id, "id")
        with self.uow_factory() as uow:
            repo = VideoGameTypeRepository(uow, VideoGameType)
            game_type = repo.get(game_type_id)
            if game_type is None:
                raise NotFoundError("Video game type not found")
            if game_type.tournaments:
                raise ValidationError("Video game type is in use")
            repo.delete(game_type)
            uow.session.flush()
            return {"deleted": True}

    def list_player_profiles(self) -> list[PlayerProfileItem]:
        with self.uow_factory() as uow:
            profiles = PlayerProfileRepository(uow, PlayerProfile).get_all()
            return [
                {
                    "nickname": profile.player.nickname,
                    "ranking_position": profile.ranking_position,
                    "total_matches": profile.total_matches,
                    "total_points": profile.total_points,
                }
                for profile in profiles
            ]

    @staticmethod
    def _named_dto(item) -> NamedCatalogItem:
        return {
            "id": item.id,
            "name": item.name,
            "description": item.description,
        }

    @staticmethod
    def _validate_name_description(name: str, description: str | None) -> None:
        CatalogService._validate_text(name, "name")
        if description is not None and not isinstance(description, str):
            raise ValidationError("description must be a string or null")
        if isinstance(description, str) and len(description) > 10000:
            raise ValidationError("description is too long")
        if len(name.strip()) > 100:
            raise ValidationError("name must be at most 100 characters")

    @staticmethod
    def _clean_description(description: str | None) -> str | None:
        if description is None:
            return None
        cleaned = description.strip()
        return cleaned or None

    @staticmethod
    def _validate_text(value: str, field: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValidationError(f"{field} must be a non-empty string")

    @staticmethod
    def _validate_id(value: int, field: str) -> None:
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValidationError(f"{field} must be a positive integer")
