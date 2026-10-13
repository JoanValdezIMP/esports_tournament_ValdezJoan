"""Business services that execute operations using server-side repositories."""

from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from logging import getLogger

from sqlalchemy import Boolean, Date, DateTime, Integer, Numeric, String, inspect

from repositories.abstract_repository import SqlAlchemyRepository
from server.entities import get_entity_models


logger = getLogger(__name__)


class CrudService:
    """Validate and execute entity CRUD operations behind the server boundary."""

    def __init__(self, uow_factory, entity_models=None):
        self.uow_factory = uow_factory
        self.entity_models = entity_models or get_entity_models()

    def list_entities(self, entity):
        model = self._model(entity)
        with self.uow_factory() as uow:
            repository = SqlAlchemyRepository(uow, model)
            return [self._to_dto(item) for item in repository.get_all()]

    def get_entity(self, entity, identifier):
        model = self._model(entity)
        key = self._identifier(model, identifier)
        with self.uow_factory() as uow:
            item = SqlAlchemyRepository(uow, model).get(key)
            if item is None:
                raise LookupError(f"{entity} record was not found.")
            return self._to_dto(item)

    def create_entity(self, entity, values):
        model = self._model(entity)
        clean_values = self._validated_values(model, values, creating=True)
        with self.uow_factory() as uow:
            repository = SqlAlchemyRepository(uow, model)
            item = model(**clean_values)
            repository.add(item)
            uow.commit()
            return self._to_dto(item)

    def update_entity(self, entity, identifier, values):
        model = self._model(entity)
        key = self._identifier(model, identifier)
        clean_values = self._validated_values(model, values, creating=False)
        if not clean_values:
            raise ValueError("Update data must contain at least one field.")

        with self.uow_factory() as uow:
            repository = SqlAlchemyRepository(uow, model)
            item = repository.get(key)
            if item is None:
                raise LookupError(f"{entity} record was not found.")
            for name, value in clean_values.items():
                setattr(item, name, value)
            if entity == "matches" and {
                "score_team_one",
                "score_team_two",
            } & clean_values.keys():
                if item.score_team_one > item.score_team_two:
                    item.id_team_winner = item.id_team_one
                elif item.score_team_two > item.score_team_one:
                    item.id_team_winner = item.id_team_two
                else:
                    item.id_team_winner = None
            uow.commit()
            return self._to_dto(item)

    def delete_entity(self, entity, identifier):
        model = self._model(entity)
        key = self._identifier(model, identifier)
        with self.uow_factory() as uow:
            repository = SqlAlchemyRepository(uow, model)
            item = repository.get(key)
            if item is None:
                raise LookupError(f"{entity} record was not found.")
            repository.delete(item)
            uow.commit()
        return {"deleted": True, "id": identifier}

    def search_players(self, nickname):
        if not isinstance(nickname, str) or not nickname.strip():
            raise ValueError("nickname must be a non-empty string.")

        from repositories import PlayerRepository

        model = self._model("players")
        with self.uow_factory() as uow:
            players = PlayerRepository(uow, model).search_by_nickname(
                nickname.strip()
            )
            return [self._to_dto(player) for player in players]

    def _model(self, entity):
        if not isinstance(entity, str) or entity not in self.entity_models:
            raise ValueError("Unknown entity.")
        return self.entity_models[entity]

    @staticmethod
    def _columns(model):
        return {
            column.key: column
            for column in inspect(model).columns
            if column.key != "last_update"
        }

    def _identifier(self, model, identifier):
        primary_keys = list(inspect(model).primary_key)
        if isinstance(identifier, dict):
            if set(identifier) != {column.key for column in primary_keys}:
                raise ValueError("Identifier must include every primary key.")
            return tuple(
                self._convert(identifier[column.key], column)
                for column in primary_keys
            ) if len(primary_keys) > 1 else self._convert(
                identifier[primary_keys[0].key], primary_keys[0]
            )

        if len(primary_keys) == 1:
            return self._convert(identifier, primary_keys[0])
        raise ValueError("Composite identifiers must be JSON objects.")

    def _validated_values(self, model, values, creating):
        if not isinstance(values, dict) or not values:
            raise ValueError("Data must be a non-empty JSON object.")

        columns = self._columns(model)
        primary_keys = {column.key for column in inspect(model).primary_key}
        unknown = set(values) - set(columns)
        if unknown:
            raise ValueError(
                f"Unknown field(s): {', '.join(sorted(unknown))}."
            )
        if not creating and set(values) & primary_keys:
            raise ValueError("Primary key fields cannot be updated.")

        converted = {}
        for name, value in values.items():
            column = columns[name]
            if (
                creating
                and column.primary_key
                and len(primary_keys) == 1
                and column.autoincrement is not False
            ):
                raise ValueError(f"{name} is generated by the server.")
            converted[name] = self._convert(value, column)
        return converted

    @staticmethod
    def _convert(value, column):
        if value is None:
            if not column.nullable and not column.primary_key:
                raise ValueError(f"{column.key} cannot be null.")
            return None

        column_type = column.type
        try:
            if isinstance(column_type, DateTime):
                if not isinstance(value, str):
                    raise ValueError(f"{column.key} must be an ISO datetime.")
                return datetime.fromisoformat(value)
            if isinstance(column_type, Date):
                if not isinstance(value, str):
                    raise ValueError(f"{column.key} must be an ISO date.")
                return date.fromisoformat(value)
            if isinstance(column_type, Boolean):
                if not isinstance(value, bool):
                    raise ValueError(f"{column.key} must be a boolean.")
                return value
            if isinstance(column_type, Integer):
                if isinstance(value, bool) or not isinstance(value, int):
                    raise ValueError(f"{column.key} must be an integer.")
                return value
            if isinstance(column_type, Numeric):
                if isinstance(value, bool) or not isinstance(
                    value, (int, float, str)
                ):
                    raise ValueError(f"{column.key} must be numeric.")
                return Decimal(str(value))
            if isinstance(column_type, String):
                if not isinstance(value, str):
                    raise ValueError(f"{column.key} must be a string.")
                if column_type.length and len(value) > column_type.length:
                    raise ValueError(
                        f"{column.key} cannot exceed "
                        f"{column_type.length} characters."
                    )
        except (ValueError, InvalidOperation) as error:
            if isinstance(error, ValueError) and str(error).startswith(
                f"{column.key} "
            ):
                raise
            raise ValueError(f"{column.key} has an invalid value.") from error
        return value

    @staticmethod
    def _to_dto(item):
        mapper = inspect(type(item))
        dto = {}
        for column in mapper.columns:
            value = getattr(item, column.key)
            if isinstance(value, (date, datetime)):
                value = value.isoformat()
            elif isinstance(value, Decimal):
                value = float(value)
            dto[column.key] = value
        return dto


def log_unexpected_error(error):
    """Record server-side details without exposing them to remote clients."""
    logger.exception("Request failed unexpectedly: %s", error)
