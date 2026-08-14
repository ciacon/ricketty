from dataclasses import FrozenInstanceError
from datetime import UTC, datetime

import pytest

from ricketty.models import Severity, StatusSnapshot


def test_status_snapshot_is_immutable_and_timestamped() -> None:
    observed_at = datetime(2026, 8, 14, 12, 0, tzinfo=UTC)
    snapshot = StatusSnapshot(
        source="tube-monitor",
        observed_at=observed_at,
        observed_monotonic=42.5,
        severity=Severity.WARNING,
        message="TUBES: MOSTLY PRESENT",
    )

    assert snapshot.source == "tube-monitor"
    assert snapshot.observed_at == observed_at
    assert snapshot.observed_monotonic == 42.5
    assert snapshot.severity is Severity.WARNING
    assert snapshot.message == "TUBES: MOSTLY PRESENT"

    with pytest.raises(FrozenInstanceError):
        snapshot.message = "TUBES: ABSOLUTELY PRESENT"  # type: ignore[misc]


def test_status_snapshot_rejects_a_naive_timestamp() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        StatusSnapshot(
            source="tube-monitor",
            observed_at=datetime(2026, 8, 14, 12, 0),
            observed_monotonic=42.5,
            severity=Severity.INFO,
            message="COUNTING TUBES",
        )
