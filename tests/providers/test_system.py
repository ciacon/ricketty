from datetime import UTC, datetime

import pytest

from ricketty.models import Severity
from ricketty.providers.system import SystemProvider


@pytest.mark.asyncio
async def test_system_provider_reports_injected_uptime_and_free_disk() -> None:
    provider = SystemProvider(
        uptime_seconds=lambda: 7_380,
        disk_free_bytes=lambda: 10 * 1024**3,
        now=lambda: datetime(2026, 8, 14, tzinfo=UTC),
        monotonic=lambda: 42.5,
    )

    snapshot = await provider.read()

    assert provider.identity.name == "system"
    assert snapshot.severity is Severity.INFO
    assert snapshot.message == "UPTIME: 2h 3m | DISK FREE: 10 GiB"


@pytest.mark.asyncio
async def test_system_provider_marks_missing_local_capabilities_as_not_available() -> None:
    provider = SystemProvider(
        uptime_seconds=lambda: None,
        disk_free_bytes=lambda: None,
        now=lambda: datetime(2026, 8, 14, tzinfo=UTC),
        monotonic=lambda: 42.5,
    )

    snapshot = await provider.read()

    assert snapshot.severity is Severity.WARNING
    assert snapshot.message == "UPTIME: N/A | DISK FREE: N/A"


@pytest.mark.asyncio
async def test_system_provider_has_safe_local_probe_defaults() -> None:
    provider = SystemProvider(now=lambda: datetime(2026, 8, 14, tzinfo=UTC), monotonic=lambda: 42.5)

    snapshot = await provider.read()

    assert snapshot.source == "system"
