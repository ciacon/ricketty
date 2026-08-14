"""Bounded local uptime and disk-space provider."""

from collections.abc import Callable
from datetime import datetime

from ricketty.models import Severity, StatusSnapshot
from ricketty.providers.base import ProviderIdentity


class SystemProvider:
    """Report local uptime and free space without network access."""

    identity = ProviderIdentity(name="system", interval_seconds=30)

    def __init__(
        self,
        *,
        uptime_seconds: Callable[[], float],
        disk_free_bytes: Callable[[], int],
        now: Callable[[], datetime],
        monotonic: Callable[[], float],
    ) -> None:
        self._uptime_seconds = uptime_seconds
        self._disk_free_bytes = disk_free_bytes
        self._now = now
        self._monotonic = monotonic

    async def read(self) -> StatusSnapshot:
        uptime_minutes = int(self._uptime_seconds()) // 60
        hours, minutes = divmod(uptime_minutes, 60)
        free_gib = self._disk_free_bytes() // 1024**3
        return StatusSnapshot(
            self.identity.name,
            self._now(),
            self._monotonic(),
            Severity.INFO,
            f"UPTIME: {hours}h {minutes}m | DISK FREE: {free_gib} GiB",
        )
