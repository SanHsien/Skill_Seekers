"""Fork regression tests: Notion 429 retries are bounded in count and total wait (F4).

A sustained 429 used to sleep and retry forever. The fake client below raises a
BaseException after many calls, so a runaway loop shows up as a failure instead of a hang.
The tests patch time.sleep and the notion_client error class, so no network is used.
"""

from __future__ import annotations

import pytest

from skill_seekers.cli import notion_scraper
from skill_seekers.cli.notion_scraper import (
    NOTION_429_MAX_RETRIES,
    NOTION_429_MAX_WAIT,
    NOTION_429_SLEEP,
    NotionToSkillConverter,
)


class _Runaway(BaseException):
    """Escapes ``except Exception`` in the scraper, so a runaway retry loop cannot be hidden."""


class _Fake429(Exception):
    status = 429


class _FakeQuery:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = 0

    def __call__(self, **_params):
        self.calls += 1
        if self.calls > 20:
            raise _Runaway(f"query called {self.calls} times")
        step = self.responses.pop(0) if len(self.responses) > 1 else self.responses[0]
        if isinstance(step, Exception):
            raise step
        return step


@pytest.fixture
def sleeps(monkeypatch):
    recorded: list[float] = []
    monkeypatch.setattr(notion_scraper.time, "sleep", lambda s: recorded.append(s))
    monkeypatch.setattr(notion_scraper, "APIResponseError", _Fake429, raising=False)
    return recorded


def _scraper(tmp_path) -> NotionToSkillConverter:
    config = {
        "name": "notion_retry",
        "database_id": "db",
        "token": "not-a-real-token",
        "output_dir": str(tmp_path / "skill"),
        "max_pages": 10,
    }
    return NotionToSkillConverter(config)


def _client_with_query(query) -> object:
    class _Databases:
        def retrieve(self, **_kwargs):
            return {"title": []}

    class _Client:
        databases = _Databases()

    _Client.databases.query = query
    return _Client()


def test_persistent_429_gives_up_after_bounded_retries(tmp_path, sleeps):
    """F4: a rate limit that never clears stops after NOTION_429_MAX_RETRIES retries."""
    query = _FakeQuery([_Fake429("rate limited")])
    client = _client_with_query(query)

    pages = _scraper(tmp_path)._extract_database_entries(client)

    assert pages == []
    assert query.calls == NOTION_429_MAX_RETRIES + 1
    assert sum(sleeps) <= NOTION_429_MAX_WAIT


def test_total_wait_budget_is_enforced_even_below_retry_count(tmp_path, sleeps, monkeypatch):
    """F4: the total wait cap applies independently of the retry count."""
    monkeypatch.setattr(notion_scraper, "NOTION_429_MAX_WAIT", NOTION_429_SLEEP * 2)
    query = _FakeQuery([_Fake429("rate limited")])
    client = _client_with_query(query)

    _scraper(tmp_path)._extract_database_entries(client)

    assert query.calls == 3
    assert sum(sleeps) <= NOTION_429_SLEEP * 2


def test_transient_429_recovers_and_succeeds(tmp_path, sleeps):
    """F4: a few 429s followed by a normal response still finish the listing."""
    empty_page = {"results": [], "has_more": False, "next_cursor": None}
    query = _FakeQuery([_Fake429("busy"), _Fake429("busy"), empty_page])
    client = _client_with_query(query)

    pages = _scraper(tmp_path)._extract_database_entries(client)

    assert pages == []
    assert query.calls == 3
    assert sleeps == [NOTION_429_SLEEP, NOTION_429_SLEEP]


class _FakeRetryAfter429(_Fake429):
    status = 429

    def __init__(self, retry_after: str):
        super().__init__("rate limited")
        self.headers = {"retry-after": retry_after}


def test_retry_after_header_sets_the_wait(tmp_path, sleeps, monkeypatch):
    """F4: a Retry-After value is honoured for the wait, not the fixed default."""
    empty_page = {"results": [], "has_more": False, "next_cursor": None}
    query = _FakeQuery([_FakeRetryAfter429("3"), _FakeRetryAfter429("3"), empty_page])
    client = _client_with_query(query)

    _scraper(tmp_path)._extract_database_entries(client)

    assert query.calls == 3
    assert sleeps == [3.0, 3.0]


def test_retry_after_longer_than_the_total_budget_gives_up_without_sleeping(tmp_path, sleeps):
    """F4: a Retry-After beyond the total wait budget ends the call rather than sleeping."""
    query = _FakeQuery([_FakeRetryAfter429(str(NOTION_429_MAX_WAIT * 10))])
    client = _client_with_query(query)

    _scraper(tmp_path)._extract_database_entries(client)

    assert query.calls == 1
    assert sleeps == []
