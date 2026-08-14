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


class Ticker:
    """Reveal one message at a time, replacing unfinished output."""

    def __init__(
        self,
        *,
        write: Callable[[str], object],
        delay_seconds: float,
        sleep: Sleep = asyncio.sleep,
    ) -> None:
        self._write = write
        self._delay_seconds = delay_seconds
        self._sleep = sleep
        self._task: asyncio.Task[None] | None = None

    def show(self, message: str) -> None:
        """Start revealing *message*, cancelling any unfinished predecessor."""
        if self._task is not None:
            self._task.cancel()
        self._task = asyncio.create_task(self._reveal(message))

    async def wait_until_idle(self) -> None:
        """Wait until the currently displayed message has finished revealing."""
        if self._task is not None:
            await self._task

    async def _reveal(self, message: str) -> None:
        await reveal(
            message,
            write=self._write,
            delay_seconds=self._delay_seconds,
            sleep=self._sleep,
        )
