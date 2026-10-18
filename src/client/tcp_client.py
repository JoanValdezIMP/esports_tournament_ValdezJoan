import json
import socket
from typing import TypedDict


class ErrorDetail(TypedDict):
    code: str
    message: str


class ClientResponse(TypedDict):
    ok: bool
    data: object | None
    error: ErrorDetail | None


class ServerConnectionError(ConnectionError):
    """Raised when the TCP server cannot be reached or stops responding."""


class ProtocolError(ValueError):
    """Raised when a server response violates the documented format."""


class TcpClient:
    def __init__(
        self,
        host: str,
        port: int,
        timeout: float = 5.0,
    ) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout

    def request(
        self, operation: str, data: dict[str, object]
    ) -> ClientResponse:
        if not isinstance(operation, str) or not operation:
            raise ValueError("operation must be a non-empty string")
        if not isinstance(data, dict):
            raise ValueError("data must be a dictionary")

        try:
            request_line = (
                json.dumps(
                    {"operation": operation, "data": data},
                    ensure_ascii=False,
                    separators=(",", ":"),
                ).encode("utf-8")
                + b"\n"
            )
        except (TypeError, ValueError) as error:
            raise ValueError(
                "request data must be JSON serializable"
            ) from error

        try:
            with socket.create_connection(
                (self.host, self.port),
                timeout=self.timeout,
            ) as connection:
                connection.sendall(request_line)
                with connection.makefile("rb") as response_stream:
                    raw_response = response_stream.readline()
        except OSError as error:
            raise ServerConnectionError(
                f"Could not communicate with server at {self.host}:{self.port}"
            ) from error

        if not raw_response or not raw_response.endswith(b"\n"):
            raise ProtocolError(
                "Server closed the connection without a complete response"
            )

        try:
            response = json.loads(raw_response.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise ProtocolError(
                "Server response must be a JSON object"
            ) from error

        return self._validate_response(response)

    @staticmethod
    def _validate_response(response: object) -> ClientResponse:
        if not isinstance(response, dict):
            raise ProtocolError("Server response must be a JSON object")
        if not {"ok", "data", "error"}.issubset(response):
            raise ProtocolError("Server response is missing required fields")

        ok = response.get("ok")
        data = response.get("data")
        error = response.get("error")
        if not isinstance(ok, bool):
            raise ProtocolError("Server response field 'ok' must be a boolean")

        if ok:
            if error is not None:
                raise ProtocolError(
                    "Successful response must have a null error"
                )
            return {"ok": True, "data": data, "error": None}

        if data is not None:
            raise ProtocolError("Failed response must have null data")
        if not isinstance(error, dict):
            raise ProtocolError("Failed response must include an error object")

        code = error.get("code")
        message = error.get("message")
        if not isinstance(code, str) or not code:
            raise ProtocolError("Error code must be a non-empty string")
        if not isinstance(message, str) or not message:
            raise ProtocolError("Error message must be a non-empty string")

        return {
            "ok": False,
            "data": None,
            "error": {"code": code, "message": message},
        }
