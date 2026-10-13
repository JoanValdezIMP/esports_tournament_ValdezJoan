"""Length-limited newline-delimited JSON protocol helpers."""

import json


MAX_MESSAGE_BYTES = 65536


class ProtocolError(ValueError):
    """Raised when a message does not conform to the wire protocol."""


def encode_message(message):
    """Serialize one JSON object and append the protocol newline."""
    if not isinstance(message, dict):
        raise ProtocolError("A protocol message must be a JSON object.")

    try:
        encoded = json.dumps(
            message, ensure_ascii=False, separators=(",", ":")
        ).encode("utf-8")
    except (TypeError, ValueError) as error:
        raise ProtocolError("Message contains non-JSON data.") from error

    if len(encoded) > MAX_MESSAGE_BYTES:
        raise ProtocolError("Message exceeds the maximum size.")
    return encoded + b"\n"


def decode_message(payload):
    """Deserialize one newline-delimited JSON object."""
    if not isinstance(payload, bytes):
        raise ProtocolError("Message data must be bytes.")
    if len(payload) > MAX_MESSAGE_BYTES:
        raise ProtocolError("Message exceeds the maximum size.")

    line = payload[:-1] if payload.endswith(b"\n") else payload
    try:
        message = json.loads(line.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ProtocolError("Message must contain valid UTF-8 JSON.") from error

    if not isinstance(message, dict):
        raise ProtocolError("A protocol message must be a JSON object.")
    return message


def read_message(reader):
    """Read one bounded JSON message from a binary file-like stream."""
    payload = reader.readline(MAX_MESSAGE_BYTES + 2)
    if not payload:
        return None
    if len(payload) > MAX_MESSAGE_BYTES + 1 or not payload.endswith(b"\n"):
        raise ProtocolError("Message is too large or missing its newline.")
    return decode_message(payload)


def write_message(writer, message):
    """Write one encoded message to a binary file-like stream."""
    writer.write(encode_message(message))
    writer.flush()
