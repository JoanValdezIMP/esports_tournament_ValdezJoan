import logging
from typing import TypedDict

from services.errors import NotFoundError, ValidationError
from services.catalog_service import CatalogService
from services.player_service import PlayerService
from services.match_service import MatchService
from services.team_service import (
    TeamService,
)
from services.tournament_service import TournamentService

logger = logging.getLogger(__name__)


class ErrorDetail(TypedDict):
    code: str
    message: str


class RouterResponse(TypedDict):
    ok: bool
    data: object | None
    error: ErrorDetail | None


class RequestRouter:
    def __init__(
        self,
        player_service: PlayerService,
        team_service: TeamService | None = None,
        catalog_service: CatalogService | None = None,
        match_service: MatchService | None = None,
        tournament_service: TournamentService | None = None,
    ) -> None:
        self.player_service = player_service
        self.team_service = team_service
        self.catalog_service = catalog_service
        self.match_service = match_service
        self.tournament_service = tournament_service

    def route(self, request: object) -> RouterResponse:
        if not isinstance(request, dict):
            return self._error(
                "invalid_request", "Request must be a JSON object"
            )

        operation = request.get("operation")
        data = request.get("data")
        if not isinstance(operation, str) or not operation:
            return self._error(
                "invalid_request",
                "Request must include a non-empty string operation",
            )
        if not isinstance(data, dict):
            return self._error(
                "invalid_request", "Request data must be a JSON object"
            )

        try:
            result = self._dispatch(operation, data)
        except ValidationError as error:
            return self._error("validation_error", str(error))
        except NotFoundError as error:
            return self._error("not_found", str(error))
        except UnknownOperationError:
            return self._error(
                "unknown_operation", "Operation is not supported"
            )
        except Exception:
            logger.exception("Failed to process operation %s", operation)
            return self._error(
                "internal_error", "An internal server error occurred"
            )

        return {"ok": True, "data": result, "error": None}

    def _dispatch(self, operation: str, data: dict) -> object:
        if operation == "players.list":
            self._validate_fields(data, set())
            return self.player_service.list_players()
        if operation == "players.search":
            self._validate_fields(data, {"nickname"})
            return self.player_service.search_players(data.get("nickname"))
        if operation == "players.read":
            self._validate_fields(data, {"id"})
            return self.player_service.get_player(data.get("id"))
        if operation == "players.create":
            allowed_fields = {
                "nickname",
                "email",
                "region_id",
                "ranking_position",
            }
            if not {"nickname", "email", "region_id"}.issubset(data):
                raise ValidationError(
                    "players.create requires nickname, email, and region_id"
                )
            if not set(data).issubset(allowed_fields):
                raise ValidationError(
                    "players.create contains unsupported fields"
                )
            return self.player_service.create_player(
                nickname=data.get("nickname"),
                email=data.get("email"),
                region_id=data.get("region_id"),
                ranking_position=data.get("ranking_position"),
            )
        if operation == "players.update":
            self._validate_fields(data, {"id", "nickname"})
            return self.player_service.update_player(
                player_id=data.get("id"),
                nickname=data.get("nickname"),
            )
        if operation == "players.delete":
            self._validate_fields(data, {"id"})
            return self.player_service.delete_player(data.get("id"))
        if operation.startswith("teams."):
            if self.team_service is None:
                raise UnknownOperationError
            return self._dispatch_team(operation, data)
        if operation.startswith(
            (
                "regions.",
                "tournament_statuses.",
                "tournament_modes.",
                "video_game_types.",
                "player_profiles.",
            )
        ):
            if self.catalog_service is None:
                raise UnknownOperationError
            return self._dispatch_catalog(operation, data)
        if operation.startswith("matches."):
            if self.match_service is None:
                raise UnknownOperationError
            return self._dispatch_match(operation, data)
        if operation.startswith("tournaments."):
            if self.tournament_service is None:
                raise UnknownOperationError
            return self._dispatch_tournament(operation, data)

        raise UnknownOperationError

    def _dispatch_match(self, operation: str, data: dict) -> object:
        if operation == "matches.list":
            self._validate_fields(data, set())
            return self.match_service.list_matches()
        if operation == "matches.create":
            fields = {
                "tournament_id",
                "team_one_id",
                "team_two_id",
                "round_number",
                "duration_minutes",
            }
            self._validate_fields(data, fields)
            return self.match_service.create_match(**data)
        if operation == "matches.update_result":
            self._validate_fields(
                data, {"id", "score_team_one", "score_team_two"}
            )
            return self.match_service.update_result(
                match_id=data.get("id"),
                score_team_one=data.get("score_team_one"),
                score_team_two=data.get("score_team_two"),
            )
        if operation == "matches.delete":
            self._validate_fields(data, {"id"})
            return self.match_service.delete_match(data.get("id"))
        raise UnknownOperationError

    def _dispatch_tournament(self, operation: str, data: dict) -> object:
        if operation == "tournaments.list":
            self._validate_fields(data, set())
            return self.tournament_service.list_tournaments()
        if operation == "tournaments.read":
            self._validate_fields(data, {"id"})
            return self.tournament_service.get_tournament(data.get("id"))
        if operation == "tournaments.create":
            fields = {
                "name",
                "start_date",
                "end_date",
                "prize_pool",
                "max_teams",
                "region_id",
                "video_game_type_id",
                "tournament_mode_id",
                "tournament_status_id",
            }
            self._validate_fields(data, fields)
            return self.tournament_service.create_tournament(**data)
        if operation == "tournaments.update":
            fields = {
                "id",
                "name",
                "start_date",
                "end_date",
                "prize_pool",
                "max_teams",
            }
            self._validate_fields(data, fields)
            return self.tournament_service.update_tournament(
                tournament_id=data.get("id"),
                name=data.get("name"),
                start_date=data.get("start_date"),
                end_date=data.get("end_date"),
                prize_pool=data.get("prize_pool"),
                max_teams=data.get("max_teams"),
            )
        if operation == "tournaments.delete":
            self._validate_fields(data, {"id"})
            return self.tournament_service.delete_tournament(data.get("id"))
        if operation == "tournaments.register_team":
            self._validate_fields(data, {"tournament_id", "team_id"})
            return self.tournament_service.register_team(
                tournament_id=data.get("tournament_id"),
                team_id=data.get("team_id"),
            )
        raise UnknownOperationError

    def _dispatch_team(self, operation: str, data: dict) -> object:
        if operation == "teams.list":
            self._validate_fields(data, set())
            return self.team_service.list_teams()
        if operation == "teams.read":
            self._validate_fields(data, {"id"})
            return self.team_service.get_team(data.get("id"))
        if operation == "teams.create":
            self._validate_fields(data, {"name", "region_id"})
            return self.team_service.create_team(
                name=data.get("name"),
                region_id=data.get("region_id"),
            )
        if operation == "teams.update":
            self._validate_fields(data, {"id", "name"})
            return self.team_service.update_team(
                team_id=data.get("id"),
                name=data.get("name"),
            )
        if operation == "teams.delete":
            self._validate_fields(data, {"id"})
            return self.team_service.delete_team(data.get("id"))
        if operation == "teams.assign_player":
            self._validate_fields(
                data,
                {"team_id", "player_id", "points_obtained"},
            )
            return self.team_service.assign_player(
                team_id=data.get("team_id"),
                player_id=data.get("player_id"),
                points_obtained=data.get("points_obtained"),
            )
        raise UnknownOperationError

    def _dispatch_catalog(self, operation: str, data: dict) -> object:
        if operation == "regions.list":
            self._validate_fields(data, set())
            return self.catalog_service.list_regions()
        if operation == "regions.create":
            self._validate_fields(data, {"name", "country_code"})
            return self.catalog_service.create_region(
                name=data.get("name"),
                country_code=data.get("country_code"),
            )
        if operation == "tournament_statuses.list":
            self._validate_fields(data, set())
            return self.catalog_service.list_tournament_statuses()
        if operation == "tournament_statuses.create":
            self._validate_optional_fields(data, {"name"}, {"description"})
            return self.catalog_service.create_tournament_status(
                name=data.get("name"),
                description=data.get("description"),
            )
        if operation == "tournament_modes.list":
            self._validate_fields(data, set())
            return self.catalog_service.list_tournament_modes()
        if operation == "tournament_modes.create":
            self._validate_optional_fields(data, {"name"}, {"description"})
            return self.catalog_service.create_tournament_mode(
                name=data.get("name"),
                description=data.get("description"),
            )
        if operation == "tournament_modes.update":
            self._validate_optional_fields(
                data, {"id", "name"}, {"description"}
            )
            return self.catalog_service.update_tournament_mode(
                mode_id=data.get("id"),
                name=data.get("name"),
                description=data.get("description"),
            )
        if operation == "tournament_modes.delete":
            self._validate_fields(data, {"id"})
            return self.catalog_service.delete_tournament_mode(data.get("id"))
        if operation == "video_game_types.list":
            self._validate_fields(data, set())
            return self.catalog_service.list_video_game_types()
        if operation == "video_game_types.create":
            self._validate_optional_fields(data, {"name"}, {"description"})
            return self.catalog_service.create_video_game_type(
                name=data.get("name"),
                description=data.get("description"),
            )
        if operation == "video_game_types.update":
            self._validate_optional_fields(
                data, {"id", "name"}, {"description"}
            )
            return self.catalog_service.update_video_game_type(
                game_type_id=data.get("id"),
                name=data.get("name"),
                description=data.get("description"),
            )
        if operation == "video_game_types.delete":
            self._validate_fields(data, {"id"})
            return self.catalog_service.delete_video_game_type(data.get("id"))
        if operation == "player_profiles.list":
            self._validate_fields(data, set())
            return self.catalog_service.list_player_profiles()
        raise UnknownOperationError

    @staticmethod
    def _validate_fields(data: dict, expected_fields: set[str]) -> None:
        if set(data) != expected_fields:
            raise ValidationError(
                f"Expected data fields: {
                    ', '.join(sorted(expected_fields)) or 'none'
                }"
            )

    @staticmethod
    def _validate_optional_fields(
        data: dict,
        required_fields: set[str],
        optional_fields: set[str],
    ) -> None:
        if not required_fields.issubset(data) or not set(data).issubset(
            required_fields | optional_fields
        ):
            expected = required_fields | optional_fields
            raise ValidationError(
                "Expected fields: "
                f"{', '.join(sorted(required_fields))}; optional fields: "
                f"{', '.join(sorted(optional_fields)) or 'none'}"
            )

    @staticmethod
    def _error(code: str, message: str) -> RouterResponse:
        return {
            "ok": False,
            "data": None,
            "error": {"code": code, "message": message},
        }


class UnknownOperationError(Exception):
    pass
