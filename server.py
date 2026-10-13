"""Start the blocking TCP server."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from domain.db import Base, engine, get_uow
import models  # noqa: F401  Registers mapped tables with Base.metadata.
from server.entities import get_entity_models
from server.router import Router
from server.services import CrudService
from server.tcp_server import DEFAULT_HOST, DEFAULT_PORT, serve_forever


if __name__ == "__main__":
    Base.metadata.create_all(engine)
    service = CrudService(get_uow, get_entity_models())
    serve_forever(
        Router(service),
        os.getenv("SERVER_HOST", DEFAULT_HOST),
        int(os.getenv("SERVER_PORT", str(DEFAULT_PORT))),
    )
