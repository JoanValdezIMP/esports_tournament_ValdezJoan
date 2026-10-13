"""Start the interactive TCP client."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from client.cli import run_client


if __name__ == "__main__":
    run_client(
        os.getenv("SERVER_HOST", "127.0.0.1"),
        int(os.getenv("SERVER_PORT", "5000")),
    )
