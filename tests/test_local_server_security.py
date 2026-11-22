"""Tests for skill_seekers.local_server_security and api/main.py exposure defaults."""

import asyncio
import importlib
import sys
from pathlib import Path

import pytest

from skill_seekers.local_server_security import (
    HostAllowlistMiddleware,
    is_loopback_host,
    resolve_allowed_hosts,
)


@pytest.mark.parametrize(
    "host, expected",
    [
        ("127.0.0.1", True),
        ("127.5.5.5", True),
        ("localhost", True),
        ("LOCALHOST", True),
        ("::1", True),
        ("[::1]", True),
        ("0.0.0.0", False),
        ("::", False),
        ("192.168.1.10", False),
        ("example.com", False),
        ("", False),
        (None, False),
    ],
)
def test_is_loopback_host(host, expected):
    assert is_loopback_host(host) is expected


def test_loopback_bind_allows_only_loopback_hosts():
    allowed = resolve_allowed_hosts("127.0.0.1", raw="")
    assert "*" not in allowed
    assert {"localhost", "127.0.0.1", "::1"} <= set(allowed)


def test_lan_bind_allows_any_host_because_operator_opted_in():
    assert resolve_allowed_hosts("0.0.0.0", raw="") == ["*"]


def test_explicit_allowlist_wins_over_bind_host():
    assert resolve_allowed_hosts("127.0.0.1", raw="Seekers.lan, [::1]") == ["seekers.lan", "::1"]


def test_env_allowlist_is_read(monkeypatch):
    monkeypatch.setenv("SKILL_SEEKERS_ALLOWED_HOSTS", "seekers.lan")
    assert resolve_allowed_hosts("127.0.0.1") == ["seekers.lan"]


def _call(middleware, host_header, scope_type="http"):
    sent = []
    reached = []

    async def inner(_scope, _receive, _send):
        reached.append(True)

    async def send(message):
        sent.append(message)

    headers = [(b"host", host_header.encode())] if host_header is not None else []
    asyncio.run(
        HostAllowlistMiddleware(inner, middleware)(
            {"type": scope_type, "headers": headers}, None, send
        )
    )
    return bool(reached), sent


@pytest.mark.parametrize("host", ["localhost", "localhost:8000", "127.0.0.1:1", "[::1]:8000"])
def test_middleware_passes_allowed_hosts(host):
    reached, _ = _call(["localhost", "127.0.0.1", "::1"], host)
    assert reached


@pytest.mark.parametrize("host", ["evil.example", "localhost.evil.example", "10.0.0.2:8000", None])
def test_middleware_rejects_other_hosts_with_400(host):
    reached, sent = _call(["localhost", "127.0.0.1", "::1"], host)
    assert not reached
    assert sent[0]["status"] == 400


def test_middleware_rejects_websocket_with_foreign_host():
    reached, sent = _call(["localhost"], "evil.example", scope_type="websocket")
    assert not reached
    assert sent[0]["type"] == "websocket.close"


def test_middleware_wildcard_allows_everything():
    reached, _ = _call(["*"], "anything.example")
    assert reached


# --- api/main.py (standalone Config API) -----------------------------------

API_DIR = Path(__file__).resolve().parent.parent / "api"


def _load_api_main(monkeypatch, cors=None):
    pytest.importorskip("fastapi")
    if cors is None:
        monkeypatch.delenv("CORS_ORIGINS", raising=False)
    else:
        monkeypatch.setenv("CORS_ORIGINS", cors)
    monkeypatch.syspath_prepend(str(API_DIR))
    for name in ("main", "config_analyzer"):
        sys.modules.pop(name, None)
    return importlib.import_module("main")


def _cleanup_api_modules():
    for name in ("main", "config_analyzer"):
        sys.modules.pop(name, None)


@pytest.fixture
def api_main(monkeypatch):
    def load(cors=None):
        return _load_api_main(monkeypatch, cors)

    yield load
    _cleanup_api_modules()


def test_api_default_cors_is_not_a_wildcard(api_main):
    module = api_main()
    assert module._cors_origins == []
    assert module._cors_credentials is False


def test_api_cors_wildcard_is_explicit_opt_in(api_main):
    module = api_main("*")
    assert module._cors_origins == ["*"]
    assert module._cors_credentials is False


def test_api_cors_explicit_origins(api_main):
    module = api_main("https://a.example, https://b.example")
    assert module._cors_origins == ["https://a.example", "https://b.example"]
    assert module._cors_credentials is True


def test_api_loopback_bind_installs_host_allowlist(api_main):
    from starlette.testclient import TestClient

    module = api_main()
    assert module.apply_loopback_host_allowlist(module.app, "127.0.0.1") is True
    client = TestClient(module.app, base_url="http://localhost")
    assert client.get("/health").status_code == 200
    assert client.get("/health", headers={"Host": "evil.example"}).status_code == 400


def test_api_lan_bind_installs_no_allowlist(api_main):
    module = api_main()
    assert module.apply_loopback_host_allowlist(module.app, "0.0.0.0") is False
