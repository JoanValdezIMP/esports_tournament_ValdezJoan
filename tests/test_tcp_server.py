import socket
from threading import Thread

from server.tcp_server import handle_client
from shared.protocol import read_message, write_message
from tests.test_router import FakeService
from server.router import Router


def test_server_handles_a_client_request_over_a_blocking_socket():
    server_socket, client_socket = socket.socketpair()
    server_thread = Thread(
        target=handle_client,
        args=(server_socket, Router(FakeService())),
    )
    server_thread.start()

    with client_socket:
        reader = client_socket.makefile("rb")
        writer = client_socket.makefile("wb")
        write_message(writer, {"operation": "list", "entity": "teams"})
        response = read_message(reader)
        writer.close()
        reader.close()

    server_thread.join(timeout=2)

    assert not server_thread.is_alive()
    assert response == {"ok": True, "data": [{"entity": "teams"}]}
