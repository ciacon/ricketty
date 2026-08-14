"""Cancellable terminal text streaming primitives."""

import asyncio
from collections.abc import Awaitable, Callable

Sleep = Callable[[float], Awaitable[object]]


async def reveal(
    text: str,
    *,
    write: Callable[[str], object],
    delay_seconds: float,
    sleep: Sleep = asyncio.sleep,
) -> None:
    """Write each successive prefix of *text* at the requested cadence."""
    for index in range(1, len(text) + 1):
        if index > 1 and delay_seconds > 0:
            await sleep(delay_seconds)
        write(text[:index])
