import os
import socket
import subprocess
import sys
import time
from pathlib import Path
from uuid import uuid4

import pytest

from client.tcp_client import TcpClient


@pytest.fixture
def running_server():
    project_root = Path(__file__).resolve().parents[1]
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as port_socket:
        port_socket.bind(("127.0.0.1", 0))
        port = port_socket.getsockname()[1]

    environment = os.environ.copy()
    environment["SERVER_HOST"] = "127.0.0.1"
    environment["SERVER_PORT"] = str(port)
    process = subprocess.Popen(
        [sys.executable, "server_main.py"],
        cwd=project_root,
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    try:
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            if process.poll() is not None:
                output = process.stdout.read() if process.stdout else ""
                pytest.fail(f"Server exited during startup:\n{output}")
            try:
                with socket.create_connection(
                    ("127.0.0.1", port), timeout=0.2
                ):
                    break
            except OSError:
                time.sleep(0.05)
        else:
            pytest.fail("Server did not start listening within 10 seconds")

        yield TcpClient("127.0.0.1", port, timeout=2)
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
        if process.stdout is not None:
            process.stdout.close()


def _request(client: TcpClient, operation: str, data: dict) -> object:
    response = client.request(operation, data)
    assert response["ok"], response["error"]
    return response["data"]


def test_server_process_supports_catalog_team_tournament_and_match_workflows(
    running_server: TcpClient,
):
    client = running_server
    suffix = uuid4().hex

    region = _request(
        client,
        "regions.create",
        {"name": f"Region-{suffix}", "country_code": "TST"},
    )
    mode = _request(
        client,
        "tournament_modes.create",
        {"name": f"Mode-{suffix}", "description": None},
    )
    status = _request(
        client,
        "tournament_statuses.create",
        {"name": f"Status-{suffix}", "description": None},
    )
    game_type = _request(
        client,
        "video_game_types.create",
        {"name": f"Game-{suffix}", "description": None},
    )
    assert region in _request(client, "regions.list", {})
    assert mode in _request(client, "tournament_modes.list", {})

    team_one = _request(
        client,
        "teams.create",
        {"name": f"TeamA-{suffix}", "region_id": region["id"]},
    )
    team_two = _request(
        client,
        "teams.create",
        {"name": f"TeamB-{suffix}", "region_id": region["id"]},
    )
    tournament = _request(
        client,
        "tournaments.create",
        {
            "name": f"Tournament-{suffix}",
            "start_date": "2026-10-19",
            "end_date": None,
            "prize_pool": "1500.50",
            "max_teams": 2,
            "region_id": region["id"],
            "video_game_type_id": game_type["id"],
            "tournament_mode_id": mode["id"],
            "tournament_status_id": status["id"],
        },
    )
    assert (
        _request(client, "tournaments.read", {"id": tournament["id"]})
        == tournament
    )
    assert tournament in _request(client, "tournaments.list", {})

    assert _request(
        client,
        "tournaments.register_team",
        {"tournament_id": tournament["id"], "team_id": team_one["id"]},
    ) == {"registered": True}
    assert _request(
        client,
        "tournaments.register_team",
        {"tournament_id": tournament["id"], "team_id": team_two["id"]},
    ) == {"registered": True}

    match = _request(
        client,
        "matches.create",
        {
            "tournament_id": tournament["id"],
            "team_one_id": team_one["id"],
            "team_two_id": team_two["id"],
            "round_number": 1,
            "duration_minutes": 45,
        },
    )
    updated_match = _request(
        client,
        "matches.update_result",
        {"id": match["id"], "score_team_one": 3, "score_team_two": 1},
    )
    assert updated_match["winner_id"] == team_one["id"]
    assert updated_match in _request(client, "matches.list", {})
    assert _request(client, "matches.delete", {"id": match["id"]}) == {
        "deleted": True
    }

    failed_delete = client.request(
        "tournaments.delete",
        {"id": tournament["id"]},
    )
    assert failed_delete["ok"] is False
    assert failed_delete["error"]["code"] == "validation_error"


def test_cli_process_creates_and_lists_region_through_tcp(
    running_server: TcpClient,
):
    project_root = Path(__file__).resolve().parents[1]
    suffix = uuid4().hex
    region_name = f"CliSmoke-{suffix}"
    environment = os.environ.copy()
    environment["SERVER_HOST"] = running_server.host
    environment["SERVER_PORT"] = str(running_server.port)

    process = subprocess.run(
        [sys.executable, "main.py"],
        cwd=project_root,
        env=environment,
        input=(
            "3\n"  # Open catalogs
            "6\n"  # Create region
            f"{region_name}\n"
            "TST\n"
            "\n"  # Continue after creation
            "1\n"  # List regions
            "\n"  # Return to catalog menu
            "0\n"  # Return to main menu
            "0\n"  # Exit
        ),
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )

    assert process.returncode == 0, process.stderr
    assert region_name in process.stdout
    assert "creada correctament" in process.stdout
