"""Async collection primitives for Ricketty providers."""

import time
from collections.abc import Callable
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
    ) -> None:
        self._now = now
        self._monotonic = monotonic

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
