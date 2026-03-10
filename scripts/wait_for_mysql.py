import os
import socket
import sys
import time


def wait_for_port(host: str, port: int, timeout_seconds: int) -> None:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=2):
                print(f"MySQL is reachable at {host}:{port}")
                return
        except OSError:
            print(f"Waiting for MySQL at {host}:{port}...")
            time.sleep(2)

    print(f"Timed out waiting for MySQL at {host}:{port}", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    db_host = os.getenv("DB_HOST", "mysql")
    db_port = int(os.getenv("DB_PORT", "3306"))
    timeout = int(os.getenv("DB_WAIT_TIMEOUT", "120"))
    wait_for_port(db_host, db_port, timeout)
