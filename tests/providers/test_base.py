from datetime import UTC, datetime

import pytest

from ricketty.models import Severity, StatusSnapshot
from ricketty.providers.base import Provider, ProviderIdentity


class FakeTubeProvider:
    identity = ProviderIdentity(name="tube-monitor", interval_seconds=5)

    async def read(self) -> StatusSnapshot:
        return StatusSnapshot(
            source=self.identity.name,
            observed_at=datetime(2026, 8, 14, 12, 0, tzinfo=UTC),
            observed_monotonic=42.5,
            severity=Severity.WARNING,
            message="TUBES: MOSTLY PRESENT",
        )


@pytest.mark.asyncio
async def test_provider_has_an_identity_and_returns_a_snapshot() -> None:
    provider = FakeTubeProvider()

    assert isinstance(provider, Provider)
    assert provider.identity.name == "tube-monitor"
    assert provider.identity.interval_seconds == 5
    assert (await provider.read()).message == "TUBES: MOSTLY PRESENT"


def test_provider_identity_rejects_non_positive_intervals() -> None:
    with pytest.raises(ValueError, match="greater than zero"):
        ProviderIdentity(name="tube-monitor", interval_seconds=0)
