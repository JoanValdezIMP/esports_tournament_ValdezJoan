import logging
import os
import sys


def main() -> None:
    sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

    import models
    from domain.db import Base, engine, get_uow
    from server.router import RequestRouter
    from server.tcp_server import run_server
    from services.catalog_service import CatalogService
    from services.match_service import MatchService
    from services.player_service import PlayerService
    from services.team_service import TeamService
    from services.tournament_service import TournamentService

    logging.basicConfig(level=logging.INFO)
    Base.metadata.create_all(engine)

    router = RequestRouter(
        PlayerService(get_uow),
        TeamService(get_uow),
        CatalogService(get_uow),
        MatchService(get_uow),
        TournamentService(get_uow),
    )
    host = os.getenv("SERVER_HOST", "127.0.0.1")
    port = int(os.getenv("SERVER_PORT", "5000"))
    run_server(host, port, router)


if __name__ == "__main__":
    main()
