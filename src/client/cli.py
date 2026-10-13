"""Interactive command-line user interface backed by the TCP client."""

import json

from client.tcp_client import TcpClient


ENTITIES = (
    "regions",
    "video_game_types",
    "tournament_modes",
    "tournament_statuses",
    "players",
    "player_profiles",
    "player_teams",
    "teams",
    "tournaments",
    "team_tournaments",
    "matches",
)


def _read_json(prompt):
    value = input(prompt)
    try:
        return json.loads(value)
    except json.JSONDecodeError as error:
        raise ValueError("Enter valid JSON.") from error


def _request_for_user(client):
    print("\nEntities: " + ", ".join(ENTITIES))
    entity = input("Entity (or 'search' for player nickname search): ").strip()
    if entity == "search":
        return client.request(
            {
                "operation": "player.search",
                "nickname": input("Nickname contains: ").strip(),
            }
        )
    if entity not in ENTITIES:
        raise ValueError("Unknown entity.")

    operation = input("Operation [list/get/create/update/delete]: ").strip()
    request = {"operation": operation, "entity": entity}
    if operation in ("get", "update", "delete"):
        request["id"] = _read_json(
            "Record ID (composite key as a JSON object): "
        )
    if operation in ("create", "update"):
        request["data"] = _read_json("Data as a JSON object: ")
    if operation not in ("list", "get", "create", "update", "delete"):
        raise ValueError("Unsupported operation.")
    return client.request(request)


def run_client(host="127.0.0.1", port=5000):
    """Run an interactive TCP client until the user exits."""
    try:
        with TcpClient(host, port) as client:
            print(f"Connected to server at {host}:{port}.")
            while True:
                try:
                    print(json.dumps(_request_for_user(client), indent=2))
                except (ValueError, ConnectionError) as error:
                    print(f"Error: {error}")
                    if isinstance(error, ConnectionError):
                        return
                should_quit = input(
                    "\nPress Enter to continue, or type 'q' to quit: "
                ).lower()
                if should_quit == "q":
                    return
    except OSError as error:
        print(f"Could not connect to {host}:{port}: {error}")
