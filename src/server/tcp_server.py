"""Blocking, single-client-at-a-time TCP server."""

import socket

from shared.protocol import ProtocolError, read_message, write_message


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 5000


def handle_client(connection, router):
    """Serve requests on a connected client until it disconnects."""
    with connection:
        reader = connection.makefile("rb")
        writer = connection.makefile("wb")
        try:
            while True:
                try:
                    request = read_message(reader)
                except ProtocolError as error:
                    write_message(
                        writer,
                        {
                            "ok": False,
                            "error": {
                                "code": "protocol_error",
                                "message": str(error),
                            },
                        },
                    )
                    break
                if request is None:
                    break
                response = router.handle(request)
                try:
                    write_message(writer, response)
                except ProtocolError:
                    write_message(
                        writer,
                        {
                            "ok": False,
                            "error": {
                                "code": "protocol_error",
                                "message": "Response exceeds the maximum size.",
                            },
                        },
                    )
        finally:
            reader.close()
            writer.close()


def serve_forever(router, host=DEFAULT_HOST, port=DEFAULT_PORT):
    """Listen and process one blocking client connection at a time."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind((host, port))
        listener.listen()
        print(f"Server listening on {host}:{port}")
        while True:
            connection, address = listener.accept()
            print(f"Client connected: {address[0]}:{address[1]}")
            handle_client(connection, router)
