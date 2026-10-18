import json
import logging
import socket
from typing import BinaryIO

from server.router import RequestRouter, RouterResponse

logger = logging.getLogger(__name__)


def handle_client(client_socket: socket.socket, router: RequestRouter) -> None:
    with client_socket.makefile("rwb") as client_stream:
        while True:
            raw_message = client_stream.readline()
            if not raw_message:
                return

            if not raw_message.endswith(b"\n"):
                _write_json_line(
                    client_stream,
                    _error_response(
                        "invalid_request",
                        "Request must end with a newline",
                    ),
                )
                return

            try:
                request = json.loads(raw_message.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                _write_json_line(
                    client_stream,
                    _error_response(
                        "invalid_request", "Request must contain valid JSON"
                    ),
                )
                continue

            response = router.route(request)
            _write_json_line(client_stream, response)


def run_server(host: str, port: int, router: RequestRouter) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((host, port))
        server_socket.listen()
        logger.info("TCP server listening on %s:%s", host, port)

        while True:
            client_socket, address = server_socket.accept()
            logger.info("Accepted client connection from %s:%s", *address)
            with client_socket:
                try:
                    handle_client(client_socket, router)
                except OSError:
                    logger.exception(
                        "Socket communication failed for %s", address
                    )


def _write_json_line(stream: BinaryIO, response: RouterResponse) -> None:
    encoded_response = json.dumps(
        response,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    stream.write(encoded_response + b"\n")
    stream.flush()


def _error_response(code: str, message: str) -> RouterResponse:
    return {
        "ok": False,
        "data": None,
        "error": {"code": code, "message": message},
    }
