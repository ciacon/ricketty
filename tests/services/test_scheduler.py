import asyncio
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


@pytest.mark.asyncio
async def test_scheduler_periodically_collects_and_coalesces_pending_updates() -> None:
    sleep_started = asyncio.Event()

    async def sleep(seconds: float) -> None:
        assert seconds == 5
        sleep_started.set()
        await asyncio.Event().wait()

    updates: asyncio.Queue[StatusSnapshot] = asyncio.Queue(maxsize=1)
    await updates.put(
        StatusSnapshot("stale", datetime(2026, 8, 14, tzinfo=UTC), 0, Severity.INFO, "STALE")
    )
    scheduler = Scheduler(monotonic=lambda: 0, sleep=sleep)
    task = asyncio.create_task(scheduler.collect_periodically(FakeProvider(), updates))

    await sleep_started.wait()

    assert (await updates.get()).message == "READY"
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task


@pytest.mark.asyncio
async def test_scheduler_runs_each_provider_until_its_owner_is_cancelled() -> None:
    all_providers_sleeping = asyncio.Event()
    sleep_calls = 0

    async def sleep(_: float) -> None:
        nonlocal sleep_calls
        sleep_calls += 1
        if sleep_calls == 2:
            all_providers_sleeping.set()
        await asyncio.Event().wait()

    updates: asyncio.Queue[StatusSnapshot] = asyncio.Queue(maxsize=2)
    scheduler = Scheduler(sleep=sleep)
    task = asyncio.create_task(scheduler.run((FakeProvider(), FailingProvider()), updates))

    await all_providers_sleeping.wait()

    assert {(await updates.get()).source, (await updates.get()).source} == {"fake", "broken-tubes"}
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
