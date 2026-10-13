"""Blocking TCP client for the JSON line protocol."""

import socket

from shared.protocol import read_message, write_message


class TcpClient:
    """Keep one TCP connection open for a sequence of requests."""

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = None
        self.reader = None
        self.writer = None

    def __enter__(self):
        self.socket = socket.create_connection((self.host, self.port))
        self.reader = self.socket.makefile("rb")
        self.writer = self.socket.makefile("wb")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.reader is not None:
            self.reader.close()
        if self.writer is not None:
            self.writer.close()
        if self.socket is not None:
            self.socket.close()

    def request(self, request):
        if self.writer is None or self.reader is None:
            raise RuntimeError("TCP client is not connected.")
        write_message(self.writer, request)
        response = read_message(self.reader)
        if response is None:
            raise ConnectionError("Server closed the connection.")
        return response
