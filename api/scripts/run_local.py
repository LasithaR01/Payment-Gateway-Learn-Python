"""Start local Redis (if needed) and the API in one command.

Usage (from api/):
  uv run python scripts/run_local.py
"""

from __future__ import annotations

import os
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path

API_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REDIS = Path(r"C:\Program Files\Redis\redis-server.exe")
REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379


def port_open(host: str, port: int, timeout: float = 0.4) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def redis_responds(host: str = REDIS_HOST, port: int = REDIS_PORT) -> bool:
    """Port open is not enough on Windows; verify Redis answers PING."""
    redis_cli = shutil.which("redis-cli")
    if redis_cli is None:
        default_cli = Path(r"C:\Program Files\Redis\redis-cli.exe")
        redis_cli = str(default_cli) if default_cli.is_file() else None
    if redis_cli is None:
        return port_open(host, port)
    try:
        result = subprocess.run(
            [redis_cli, "-h", host, "-p", str(port), "ping"],
            capture_output=True,
            text=True,
            timeout=3,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return result.stdout.strip().upper() == "PONG"


def find_redis_server() -> Path | None:
    env_path = os.environ.get("REDIS_SERVER")
    if env_path and Path(env_path).is_file():
        return Path(env_path)
    which = shutil.which("redis-server")
    if which:
        return Path(which)
    if DEFAULT_REDIS.is_file():
        return DEFAULT_REDIS
    return None


def ensure_redis() -> subprocess.Popen[bytes] | None:
    if redis_responds():
        print(f"Redis already running on {REDIS_HOST}:{REDIS_PORT}")
        return None

    if port_open(REDIS_HOST, REDIS_PORT):
        print(
            f"Port {REDIS_PORT} is open but Redis did not answer PING.\n"
            "On Windows this often means ephemeral ports are exhausted after\n"
            "earlier hung reconnects. Restart the Redis service, wait ~30s,\n"
            "then retry:\n"
            "  net stop Redis\n"
            "  net start Redis",
            file=sys.stderr,
        )
        sys.exit(1)

    redis_server = find_redis_server()
    if redis_server is None:
        print(
            "Redis is not running and redis-server was not found.\n"
            "Install Redis for Windows, then retry.\n"
            "  winget install Redis.Redis",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"Starting Redis: {redis_server}")
    proc = subprocess.Popen(
        [str(redis_server)],
        cwd=str(redis_server.parent),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    for _ in range(40):
        if redis_responds():
            print(f"Redis is up on {REDIS_HOST}:{REDIS_PORT}")
            return proc
        if proc.poll() is not None:
            break
        time.sleep(0.25)

    print("Redis did not become ready on port 6379.", file=sys.stderr)
    proc.terminate()
    sys.exit(1)


def main() -> None:
    os.chdir(API_ROOT)
    redis_proc = ensure_redis()
    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "main:app",
        "--ws",
        "websockets-sansio",
        "--timeout-graceful-shutdown",
        "1",
        "--reload",
    ]
    print("Starting API:", " ".join(cmd))
    try:
        raise SystemExit(subprocess.call(cmd))
    finally:
        if redis_proc is not None and redis_proc.poll() is None:
            print("Stopping Redis started by this script...")
            redis_proc.terminate()
            try:
                redis_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                redis_proc.kill()


if __name__ == "__main__":
    main()
