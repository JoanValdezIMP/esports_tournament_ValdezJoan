from server.router import Router


class FakeService:
    def list_entities(self, entity):
        return [{"entity": entity}]

    def get_entity(self, entity, identifier):
        return {"entity": entity, "id": identifier}

    def create_entity(self, entity, values):
        return {"entity": entity, **values}

    def update_entity(self, entity, identifier, values):
        return {"entity": entity, "id": identifier, **values}

    def delete_entity(self, entity, identifier):
        return {"deleted": True, "id": identifier}

    def search_players(self, nickname):
        return [{"nickname": nickname}]


def test_router_dispatches_crud_and_search_requests():
    router = Router(FakeService())

    assert router.handle({"operation": "list", "entity": "teams"}) == {
        "ok": True,
        "data": [{"entity": "teams"}],
    }
    assert router.handle(
        {"operation": "get", "entity": "teams", "id": 4}
    )["data"]["id"] == 4
    assert router.handle(
        {"operation": "create", "entity": "teams", "data": {"name": "A"}}
    )["data"]["name"] == "A"
    assert router.handle(
        {
            "operation": "update",
            "entity": "teams",
            "id": 4,
            "data": {"name": "B"},
        }
    )["data"]["name"] == "B"
    assert router.handle(
        {"operation": "delete", "entity": "teams", "id": 4}
    )["data"]["deleted"] is True
    assert router.handle(
        {"operation": "player.search", "nickname": "Blue"}
    )["data"] == [{"nickname": "Blue"}]


def test_router_rejects_missing_extra_and_unsupported_fields():
    router = Router(FakeService())

    missing = router.handle({"operation": "get", "entity": "teams"})
    extra = router.handle(
        {"operation": "list", "entity": "teams", "unexpected": True}
    )
    unsupported = router.handle(
        {"operation": "drop", "entity": "teams"}
    )

    assert missing["error"]["code"] == "invalid_request"
    assert extra["error"]["code"] == "invalid_request"
    assert unsupported["error"]["code"] == "invalid_request"


def test_router_maps_missing_records_to_not_found():
    class MissingService(FakeService):
        def get_entity(self, entity, identifier):
            raise LookupError("record missing")

    response = Router(MissingService()).handle(
        {"operation": "get", "entity": "teams", "id": 1}
    )

    assert response == {
        "ok": False,
        "error": {"code": "not_found", "message": "record missing"},
    }
