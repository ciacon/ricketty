"""Bounded local uptime and disk-space provider."""

import shutil
import time
from collections.abc import Callable
from datetime import datetime
from pathlib import Path

from ricketty.models import Severity, StatusSnapshot
from ricketty.providers.base import ProviderIdentity


def local_uptime_seconds() -> float | None:
    """Read Linux uptime when available without making it a hard dependency."""
    try:
        return float(Path("/proc/uptime").read_text().split()[0])
    except OSError, ValueError, IndexError:
        return None


def local_disk_free_bytes() -> int | None:
    """Read free space for the home filesystem with a safe fallback."""
    try:
        return shutil.disk_usage(Path.home()).free
    except OSError:
        return None


class SystemProvider:
    """Report local uptime and free space without network access."""

    identity = ProviderIdentity(name="system", interval_seconds=30)

    def __init__(
        self,
        *,
        uptime_seconds: Callable[[], float | None] = local_uptime_seconds,
        disk_free_bytes: Callable[[], int | None] = local_disk_free_bytes,
        now: Callable[[], datetime] = lambda: datetime.now().astimezone(),
        monotonic: Callable[[], float] = time.monotonic,
    ) -> None:
        self._uptime_seconds = uptime_seconds
        self._disk_free_bytes = disk_free_bytes
        self._now = now
        self._monotonic = monotonic

    async def read(self) -> StatusSnapshot:
        uptime_seconds = self._uptime_seconds()
        disk_free_bytes = self._disk_free_bytes()
        uptime = "N/A"
        disk_free = "N/A"
        severity = Severity.WARNING
        if uptime_seconds is not None:
            uptime_minutes = int(uptime_seconds) // 60
            hours, minutes = divmod(uptime_minutes, 60)
            uptime = f"{hours}h {minutes}m"
        if disk_free_bytes is not None:
            disk_free = f"{disk_free_bytes // 1024**3} GiB"
        if uptime_seconds is not None and disk_free_bytes is not None:
            severity = Severity.INFO
        return StatusSnapshot(
            self.identity.name,
            self._now(),
            self._monotonic(),
            severity,
            f"UPTIME: {uptime} | DISK FREE: {disk_free}",
        )
