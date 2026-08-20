from datetime import UTC, datetime

import pytest

from ricketty.providers.bulletins import BulletinProvider


@pytest.mark.asyncio
async def test_bulletin_provider_cycles_deterministically() -> None:
    provider = BulletinProvider(
        bulletins=("TUBES: MOSTLY PRESENT", "RADIO: RECEIVING VIBES"),
        now=lambda: datetime(2026, 8, 14, tzinfo=UTC),
        monotonic=lambda: 42.5,
    )

    assert (await provider.read()).message == "TUBES: MOSTLY PRESENT"
    assert (await provider.read()).message == "RADIO: RECEIVING VIBES"
    assert (await provider.read()).message == "TUBES: MOSTLY PRESENT"


@pytest.mark.asyncio
async def test_bulletin_provider_has_local_defaults() -> None:
    provider = BulletinProvider(
        now=lambda: datetime(2026, 8, 14, tzinfo=UTC), monotonic=lambda: 42.5
    )

    snapshot = await provider.read()

    assert snapshot.source == "bulletins"
    assert snapshot.message
