"""Shared guards for the unauthenticated local HTTP servers.

The embedding server (and anything else that spends the user's provider API
quota or touches local files) has no authentication. The only things standing
between it and a hostile web page or LAN host are where it binds, which
browser origins may read its responses, and which ``Host`` header it accepts.

Defaults here are loopback-only:

- bind host: ``127.0.0.1``; a non-loopback bind is an explicit opt-in
  (``--host`` flag or ``EMBEDDING_HOST`` environment variable);
- ``Host`` allowlist: when bound to loopback, only ``localhost``, ``127.0.0.1``
  and ``::1`` are served, which blocks DNS-rebinding from a browser;
  override with ``SKILL_SEEKERS_ALLOWED_HOSTS`` (comma separated, ``*`` = any).
"""

from __future__ import annotations

import ipaddress
import os

DEFAULT_BIND_HOST = "127.0.0.1"
LOOPBACK_ALLOWED_HOSTS = ["localhost", "127.0.0.1", "::1"]
ALLOWED_HOSTS_ENV = "SKILL_SEEKERS_ALLOWED_HOSTS"


def is_loopback_host(host: str | None) -> bool:
    """True only for ``localhost`` or a loopback IP literal (v4 or v6)."""
    if not host:
        return False
    host = host.strip().strip("[]").lower()
    if host == "localhost":
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def resolve_allowed_hosts(bind_host: str | None, raw: str | None = None) -> list[str]:
    """Return the ``Host`` allowlist for a server bound to ``bind_host``.

    An explicit ``SKILL_SEEKERS_ALLOWED_HOSTS`` value always wins. Otherwise a
    loopback bind allows only loopback names and a non-loopback bind (the
    operator opted in to the network) allows any host.
    """
    if raw is None:
        raw = os.environ.get(ALLOWED_HOSTS_ENV, "")
    explicit = [h.strip().strip("[]").lower() for h in raw.split(",") if h.strip()]
    if explicit:
        return explicit
    if is_loopback_host(bind_host):
        return list(LOOPBACK_ALLOWED_HOSTS)
    return ["*"]


def _host_name(host_header: str) -> str:
    """Strip the port from a Host header value, handling ``[::1]:8000``."""
    host_header = host_header.strip().lower()
    if host_header.startswith("["):
        end = host_header.find("]")
        return host_header[1:end] if end != -1 else host_header
    return host_header.rsplit(":", 1)[0] if host_header.count(":") == 1 else host_header


class HostAllowlistMiddleware:
    """Pure-ASGI middleware answering 400 when the Host header is not allowed."""

    def __init__(self, app, allowed_hosts: list[str]):
        self.app = app
        self.allow_any = "*" in allowed_hosts
        self.allowed = {h.lower() for h in allowed_hosts}

    async def __call__(self, scope, receive, send):
        if scope["type"] not in ("http", "websocket") or self.allow_any:
            await self.app(scope, receive, send)
            return
        headers = dict(scope.get("headers") or [])
        host = _host_name(headers.get(b"host", b"").decode("latin-1"))
        if host in self.allowed:
            await self.app(scope, receive, send)
            return
        if scope["type"] == "websocket":
            await send({"type": "websocket.close", "code": 1008})
            return
        body = b"Invalid host header"
        await send(
            {
                "type": "http.response.start",
                "status": 400,
                "headers": [
                    (b"content-type", b"text/plain; charset=utf-8"),
                    (b"content-length", str(len(body)).encode()),
                ],
            }
        )
        await send({"type": "http.response.body", "body": body})
