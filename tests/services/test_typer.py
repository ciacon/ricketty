import asyncio
from collections.abc import Callable

import pytest

from ricketty.services.typer import Ticker, reveal


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


@pytest.mark.asyncio
async def test_ticker_replaces_an_unfinished_message() -> None:
    seen: list[str] = []
    release_glyphs = asyncio.Event()

    async def wait_for_release(_: float) -> None:
        await release_glyphs.wait()

    ticker = Ticker(write=seen.append, delay_seconds=1, sleep=wait_for_release)

    ticker.show("OLD")
    await asyncio.sleep(0)
    ticker.show("NEW")
    release_glyphs.set()
    await ticker.wait_until_idle()

    assert seen == ["O", "N", "NE", "NEW"]
