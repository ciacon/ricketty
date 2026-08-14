from datetime import UTC, datetime

import pytest

from ricketty.models import Severity, StatusSnapshot
from ricketty.providers.base import ProviderIdentity
from ricketty.services.scheduler import Scheduler


class FakeProvider:
    identity = ProviderIdentity(name="fake", interval_seconds=5)

    async def read(self) -> StatusSnapshot:
        return StatusSnapshot(
            "fake", datetime(2026, 8, 14, tzinfo=UTC), 42.5, Severity.INFO, "READY"
        )


class FailingProvider:
    identity = ProviderIdentity(name="broken-tubes", interval_seconds=5)

    async def read(self) -> StatusSnapshot:
        raise RuntimeError("tube collapse")


@pytest.mark.asyncio
async def test_scheduler_collects_a_snapshot_from_a_provider() -> None:
    scheduler = Scheduler()

    snapshot = await scheduler.collect_once(FakeProvider())

    assert snapshot.message == "READY"


@pytest.mark.asyncio
async def test_scheduler_turns_a_provider_failure_into_an_error_snapshot() -> None:
    scheduler = Scheduler(now=lambda: datetime(2026, 8, 14, tzinfo=UTC), monotonic=lambda: 42.5)

    snapshot = await scheduler.collect_once(FailingProvider())

    assert snapshot.source == "broken-tubes"
    assert snapshot.severity is Severity.ERROR
    assert snapshot.message == "PROVIDER FAILURE: tube collapse"
