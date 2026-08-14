from collections.abc import Callable

import pytest

from ricketty.services.typer import reveal


@pytest.mark.asyncio
async def test_reveal_writes_each_successive_prefix() -> None:
    seen: list[str] = []
    sink: Callable[[str], None] = seen.append

    await reveal("OK", write=sink, delay_seconds=0)

    assert seen == ["O", "OK"]


@pytest.mark.asyncio
async def test_reveal_waits_only_between_successive_prefixes() -> None:
    seen: list[str] = []
    delays: list[float] = []

    async def record_delay(seconds: float) -> None:
        delays.append(seconds)

    await reveal("OK", write=seen.append, delay_seconds=0.25, sleep=record_delay)

    assert seen == ["O", "OK"]
    assert delays == [0.25]
