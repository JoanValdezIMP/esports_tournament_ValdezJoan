import json
import socket
import threading
from unittest.mock import MagicMock, patch

import pytest

from client.tcp_client import ProtocolError, ServerConnectionError, TcpClient
from server.router import RequestRouter
from server.tcp_server import handle_client


def _handle_client_and_close(server_socket, router):
    try:
        handle_client(server_socket, router)
    finally:
        server_socket.close()


def _server_that_sends(response_bytes):
    client_socket, server_socket = socket.socketpair()

    def send_response():
        with server_socket:
            server_socket.recv(4096)
            server_socket.sendall(response_bytes)

    thread = threading.Thread(target=send_response)
    thread.start()
    return client_socket, thread


def test_tcp_client_serializes_request_and_deserializes_server_response():
    client_socket, server_thread_socket = socket.socketpair()
    service = MagicMock()
    service.list_players.return_value = [
        {
            "id": 1,
            "nickname": "PlayerOne",
            "region": "Europe",
            "has_profile": True,
        }
    ]
    router = RequestRouter(service)
    server_thread = threading.Thread(
        target=_handle_client_and_close,
        args=(server_thread_socket, router),
    )
    server_thread.start()

    with patch(
        "client.tcp_client.socket.create_connection",
        return_value=client_socket,
    ):
        response = TcpClient("localhost", 5000).request("players.list", {})

    server_thread.join(timeout=2)
    assert not server_thread.is_alive()
    assert response == {
        "ok": True,
        "data": [
            {
                "id": 1,
                "nickname": "PlayerOne",
                "region": "Europe",
                "has_profile": True,
            }
        ],
        "error": None,
    }


def test_tcp_client_returns_valid_server_error_response():
    client_socket, server_thread = _server_that_sends(
        b'{"ok":false,"data":null,"error":{"code":"unknown_operation",'
        b'"message":"Operation is not supported"}}\n'
    )

    with patch(
        "client.tcp_client.socket.create_connection",
        return_value=client_socket,
    ):
        response = TcpClient("localhost", 5000).request("teams.list", {})

    server_thread.join(timeout=2)
    assert response == {
        "ok": False,
        "data": None,
        "error": {
            "code": "unknown_operation",
            "message": "Operation is not supported",
        },
    }


@pytest.mark.parametrize(
    "response_bytes",
    [
        b"{not json}\n",
        b'{"ok":true,"data":[]}\n',
        b'{"ok":"yes","data":[],"error":null}\n',
        b'{"ok":false,"data":[],"error":{"code":"bad","message":"Bad"}}\n',
        b'{"ok":true,"data":[],"error":null}',
    ],
)
def test_tcp_client_rejects_invalid_server_responses(response_bytes):
    client_socket, server_thread = _server_that_sends(response_bytes)

    with (
        patch(
            "client.tcp_client.socket.create_connection",
            return_value=client_socket,
        ),
        pytest.raises(ProtocolError),
    ):
        TcpClient("localhost", 5000).request("players.list", {})

    server_thread.join(timeout=2)
    assert not server_thread.is_alive()


def test_tcp_client_raises_clear_error_when_connection_fails():
    with (
        patch(
            "client.tcp_client.socket.create_connection",
            side_effect=OSError("connection refused"),
        ),
        pytest.raises(
            ServerConnectionError, match="Could not communicate with server"
        ),
    ):
        TcpClient("localhost", 5000).request("players.list", {})


def test_tcp_client_rejects_non_json_request_data_before_connecting():
    with patch(
        "client.tcp_client.socket.create_connection"
    ) as create_connection:
        with pytest.raises(ValueError, match="JSON serializable"):
            TcpClient("localhost", 5000).request(
                "players.list",
                {"invalid": object()},
            )

    create_connection.assert_not_called()
