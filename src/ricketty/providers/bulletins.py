"""Deterministic local bulletin source."""

import time
from collections.abc import Callable
from datetime import datetime

from ricketty.models import Severity, StatusSnapshot
from ricketty.providers.base import ProviderIdentity

DEFAULT_BULLETINS = (
    "RADIO: RECEIVING VIBES",
    "TUBES: MOSTLY PRESENT",
    "COFFEE LEVEL: THEORETICAL",
)


class BulletinProvider:
    """Cycle through supplied local bulletins without network access."""

    identity = ProviderIdentity(name="bulletins", interval_seconds=15)

    def __init__(
        self,
        *,
        bulletins: tuple[str, ...] = DEFAULT_BULLETINS,
        now: Callable[[], datetime] = lambda: datetime.now().astimezone(),
        monotonic: Callable[[], float] = time.monotonic,
    ) -> None:
        self._bulletins = bulletins
        self._now = now
        self._monotonic = monotonic
        self._index = 0

    async def read(self) -> StatusSnapshot:
        message = self._bulletins[self._index % len(self._bulletins)]
        self._index += 1
        return StatusSnapshot(
            self.identity.name, self._now(), self._monotonic(), Severity.INFO, message
        )
