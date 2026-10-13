import io

import pytest

from shared.protocol import (
    MAX_MESSAGE_BYTES,
    ProtocolError,
    decode_message,
    encode_message,
    read_message,
    write_message,
)


def test_message_round_trip_and_stream_helpers():
    message = {"operation": "list", "entity": "teams", "name": "Àguila"}
    encoded = encode_message(message)

    assert encoded.endswith(b"\n")
    assert decode_message(encoded) == message

    stream = io.BytesIO()
    write_message(stream, message)
    stream.seek(0)
    assert read_message(stream) == message
    assert read_message(stream) is None


@pytest.mark.parametrize(
    "payload",
    [b"{bad json}\n", b'["not", "an object"]\n', b"\xff\n"],
)
def test_decode_rejects_invalid_messages(payload):
    with pytest.raises(ProtocolError):
        decode_message(payload)


def test_encode_rejects_oversized_message():
    with pytest.raises(ProtocolError, match="maximum size"):
        encode_message({"payload": "x" * MAX_MESSAGE_BYTES})


def test_read_rejects_missing_newline():
    with pytest.raises(ProtocolError, match="missing its newline"):
        read_message(io.BytesIO(b'{"ok":true}'))
