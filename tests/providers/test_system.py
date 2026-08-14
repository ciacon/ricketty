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
