from datetime import UTC, datetime

import pytest

from ricketty.models import Severity
from ricketty.providers.clock import ClockProvider


@pytest.mark.asyncio
async def test_clock_provider_reports_an_injected_timezone_aware_time() -> None:
    observed_at = datetime(2026, 8, 14, 12, 34, 56, tzinfo=UTC)
    provider = ClockProvider(now=lambda: observed_at, monotonic=lambda: 42.5)

    snapshot = await provider.read()

    assert provider.identity.name == "clock"
    assert snapshot.source == "clock"
    assert snapshot.observed_at == observed_at
    assert snapshot.observed_monotonic == 42.5
    assert snapshot.severity is Severity.INFO
    assert snapshot.message == "2026-08-14 12:34:56 UTC"
