"""Request validation and dispatch for the JSON-over-TCP API."""

from server.services import log_unexpected_error


class Router:
    """Route validated request dictionaries to the business service."""

    def __init__(self, service):
        self.service = service

    def handle(self, request):
        if not isinstance(request, dict):
            return self._error("invalid_request", "Request must be an object.")

        operation = request.get("operation")
        entity = request.get("entity")
        try:
            if operation == "player.search":
                self._require_keys(request, {"operation", "nickname"})
                data = self.service.search_players(request["nickname"])
            else:
                if not isinstance(entity, str):
                    raise ValueError("entity must be a string.")
                if operation == "list":
                    self._require_keys(request, {"operation", "entity"})
                    data = self.service.list_entities(entity)
                elif operation == "get":
                    self._require_keys(
                        request, {"operation", "entity", "id"}
                    )
                    data = self.service.get_entity(entity, request["id"])
                elif operation == "create":
                    self._require_keys(
                        request, {"operation", "entity", "data"}
                    )
                    data = self.service.create_entity(
                        entity, request["data"]
                    )
                elif operation == "update":
                    self._require_keys(
                        request, {"operation", "entity", "id", "data"}
                    )
                    data = self.service.update_entity(
                        entity, request["id"], request["data"]
                    )
                elif operation == "delete":
                    self._require_keys(
                        request, {"operation", "entity", "id"}
                    )
                    data = self.service.delete_entity(
                        entity, request["id"]
                    )
                else:
                    raise ValueError("Unsupported operation.")
            return {"ok": True, "data": data}
        except (KeyError, TypeError, ValueError) as error:
            return self._error("invalid_request", str(error))
        except LookupError as error:
            return self._error("not_found", str(error))
        except Exception as error:
            log_unexpected_error(error)
            return self._error("internal_error", "The request could not be completed.")

    @staticmethod
    def _require_keys(request, required):
        if set(request) != required:
            raise ValueError(
                "Request fields must be exactly: "
                + ", ".join(sorted(required))
                + "."
            )

    @staticmethod
    def _error(code, message):
        return {"ok": False, "error": {"code": code, "message": message}}
