"""Typed, renderer-independent data carried through Ricketty."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class Severity(StrEnum):
    """How urgently a status message should be presented."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class StatusSnapshot:
    """An immutable observation supplied by one Ricketty data source."""

    source: str
    observed_at: datetime
    observed_monotonic: float
    severity: Severity
    message: str

    def __post_init__(self) -> None:
        if self.observed_at.tzinfo is None or self.observed_at.utcoffset() is None:
            msg = "observed_at must be timezone-aware"
            raise ValueError(msg)
