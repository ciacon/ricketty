"""Async collection primitives for Ricketty providers."""

import asyncio
import time
from collections.abc import Awaitable, Callable, Iterable
from datetime import datetime

from ricketty.models import Severity, StatusSnapshot
from ricketty.providers.base import Provider


class Scheduler:
    """Collect provider observations without coupling them to the UI."""

    def __init__(
        self,
        *,
        now: Callable[[], datetime] = lambda: datetime.now().astimezone(),
        monotonic: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
    ) -> None:
        self._now = now
        self._monotonic = monotonic
        self._sleep = sleep

    async def collect_once(self, provider: Provider) -> StatusSnapshot:
        """Collect one current observation, preserving a failed provider as status."""
        try:
            return await provider.read()
        except Exception as error:
            return StatusSnapshot(
                source=provider.identity.name,
                observed_at=self._now(),
                observed_monotonic=self._monotonic(),
                severity=Severity.ERROR,
                message=f"PROVIDER FAILURE: {error}",
            )

    async def collect_periodically(
        self, provider: Provider, updates: asyncio.Queue[StatusSnapshot]
    ) -> None:
        """Publish current provider observations at a monotonic cadence forever."""
        next_deadline = self._monotonic()
        while True:
            snapshot = await self.collect_once(provider)
            self._coalesce_put(updates, snapshot)

            next_deadline += provider.identity.interval_seconds
            await self._sleep(max(0, next_deadline - self._monotonic()))

    async def run(
        self, providers: Iterable[Provider], updates: asyncio.Queue[StatusSnapshot]
    ) -> None:
        """Own one periodic collection task per provider until cancelled."""
        async with asyncio.TaskGroup() as tasks:
            for provider in providers:
                tasks.create_task(self.collect_periodically(provider, updates))

    @staticmethod
    def _coalesce_put(updates: asyncio.Queue[StatusSnapshot], snapshot: StatusSnapshot) -> None:
        if updates.full():
            updates.get_nowait()
        updates.put_nowait(snapshot)
