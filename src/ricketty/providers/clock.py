"""A local wall-clock provider."""

import time
from collections.abc import Callable
from datetime import datetime

from ricketty.models import Severity, StatusSnapshot
from ricketty.providers.base import ProviderIdentity


class ClockProvider:
    """Report the current local wall clock through the provider contract."""

    identity = ProviderIdentity(name="clock", interval_seconds=1)

    def __init__(
        self,
        *,
        now: Callable[[], datetime] = lambda: datetime.now().astimezone(),
        monotonic: Callable[[], float] = time.monotonic,
    ) -> None:
        self._now = now
        self._monotonic = monotonic

    async def read(self) -> StatusSnapshot:
        observed_at = self._now()
        return StatusSnapshot(
            source=self.identity.name,
            observed_at=observed_at,
            observed_monotonic=self._monotonic(),
            severity=Severity.INFO,
            message=observed_at.strftime("%Y-%m-%d %H:%M:%S %Z"),
        )
