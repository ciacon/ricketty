"""Common contracts for independent Ricketty data sources."""

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from ricketty.models import StatusSnapshot


@dataclass(frozen=True, slots=True)
class ProviderIdentity:
    """Stable metadata used to identify and schedule a provider."""

    name: str
    interval_seconds: float

    def __post_init__(self) -> None:
        if not self.name:
            msg = "name must not be empty"
            raise ValueError(msg)
        if self.interval_seconds <= 0:
            msg = "interval_seconds must be greater than zero"
            raise ValueError(msg)


@runtime_checkable
class Provider(Protocol):
    """A source that asynchronously observes one current status snapshot."""

    identity: ProviderIdentity

    async def read(self) -> StatusSnapshot:
        """Return the provider's most recent observation."""
        ...
