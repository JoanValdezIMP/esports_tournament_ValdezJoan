import json
import socket
import threading
from unittest.mock import MagicMock

from server.tcp_server import handle_client


def _handle_client_and_close(client_socket, router):
    try:
        handle_client(client_socket, router)
    finally:
        client_socket.close()


def _exchange_messages(messages):
    server_socket, client_socket = socket.socketpair()
    router = MagicMock()
    router.route.side_effect = [
        {"ok": True, "data": [], "error": None},
    ]
    server_thread = threading.Thread(
        target=_handle_client_and_close,
        args=(server_socket, router),
    )
    server_thread.start()

    try:
        client_socket.sendall(messages)
        client_socket.shutdown(socket.SHUT_WR)
        with client_socket.makefile("rb") as client_stream:
            responses = [json.loads(line) for line in client_stream]
    finally:
        client_socket.close()
        server_socket.close()
        server_thread.join(timeout=2)

    assert not server_thread.is_alive()
    return responses, router


def test_tcp_server_routes_json_line_and_returns_json_line():
    responses, router = _exchange_messages(
        b'{"operation":"players.list","data":{}}\n'
    )

    assert responses == [{"ok": True, "data": [], "error": None}]
    router.route.assert_called_once_with(
        {"operation": "players.list", "data": {}}
    )


def test_tcp_server_answers_invalid_json_and_continues_reading():
    server_socket, client_socket = socket.socketpair()
    router = MagicMock()
    router.route.return_value = {"ok": True, "data": [], "error": None}
    server_thread = threading.Thread(
        target=_handle_client_and_close,
        args=(server_socket, router),
    )
    server_thread.start()

    try:
        client_socket.sendall(
            b'{not json}\n{"operation":"players.list","data":{}}\n'
        )
        client_socket.shutdown(socket.SHUT_WR)
        with client_socket.makefile("rb") as client_stream:
            responses = [json.loads(line) for line in client_stream]
    finally:
        client_socket.close()
        server_socket.close()
        server_thread.join(timeout=2)

    assert not server_thread.is_alive()
    assert responses == [
        {
            "ok": False,
            "data": None,
            "error": {
                "code": "invalid_request",
                "message": "Request must contain valid JSON",
            },
        },
        {"ok": True, "data": [], "error": None},
    ]
    router.route.assert_called_once_with(
        {"operation": "players.list", "data": {}}
    )


def test_tcp_server_rejects_unterminated_message():
    responses, router = _exchange_messages(
        b'{"operation":"players.list","data":{}}'
    )

    assert responses == [
        {
            "ok": False,
            "data": None,
            "error": {
                "code": "invalid_request",
                "message": "Request must end with a newline",
            },
        }
    ]
    router.route.assert_not_called()
