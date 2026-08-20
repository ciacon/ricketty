"""The first Ricketty terminal application."""

import asyncio

from textual.app import App, ComposeResult
from textual.widgets import Static

from ricketty.models import StatusSnapshot
from ricketty.providers.base import Provider
from ricketty.providers.bulletins import BulletinProvider
from ricketty.providers.clock import ClockProvider
from ricketty.providers.system import SystemProvider
from ricketty.services.scheduler import Scheduler
from ricketty.services.typer import Ticker

DEFAULT_BOOT_MESSAGES = (
    "RICKETTY BIOS // REV 0.1",
    "PROBING TUBE INTEGRITY",
    "TUBES: MOSTLY PRESENT",
    "RICKETTY TERMINAL ONLINE",
)
DEFAULT_MESSAGE_PAUSE_SECONDS = 1.5


class RickettyApp(App[None]):
    """A fullscreen terminal screen that slowly reveals boot text."""

    BINDINGS = [("ctrl+c", "quit", "Quit"), ("ctrl+q", "quit", "Quit")]
    CSS_PATH = "styles.tcss"
    TITLE = "RICKETTY"

    def __init__(
        self,
        *,
        boot_messages: tuple[str, ...] = DEFAULT_BOOT_MESSAGES,
        glyph_delay_seconds: float = 0.04,
        message_pause_seconds: float = DEFAULT_MESSAGE_PAUSE_SECONDS,
        updates: asyncio.Queue[StatusSnapshot] | None = None,
        providers: tuple[Provider, ...] | None = None,
    ) -> None:
        super().__init__()
        self._boot_messages = boot_messages
        self._glyph_delay_seconds = glyph_delay_seconds
        self._message_pause_seconds = message_pause_seconds
        self._updates = updates or asyncio.Queue(maxsize=1)
        self._providers = (
            (ClockProvider(), SystemProvider(), BulletinProvider())
            if providers is None
            else providers
        )

    def compose(self) -> ComposeResult:
        yield Static("CLOCK: INITIALIZING", id="clock")
        yield Static("SYSTEM: INITIALIZING", id="system")
        yield Static("BULLETINS: INITIALIZING", id="bulletins")
        yield Static("EVENT LOG: BOOTING", id="event-log")
        yield Static("", id="ticker")

    def on_mount(self) -> None:
        self.run_worker(self._reveal_boot_messages(), name="boot-messages", exclusive=True)
        self.run_worker(
            self._render_updates(), name="render-updates", group="updates", exclusive=True
        )
        self.run_worker(
            Scheduler().run(self._providers, self._updates),
            name="provider-scheduler",
            group="providers",
            exclusive=True,
        )

    async def _reveal_boot_messages(self) -> None:
        ticker = self.query_one("#ticker", Static)
        boot_ticker = Ticker(
            write=ticker.update,
            delay_seconds=self._glyph_delay_seconds,
        )
        last_message_index = len(self._boot_messages) - 1
        for index, message in enumerate(self._boot_messages):
            boot_ticker.show(message)
            await boot_ticker.wait_until_idle()
            if index < last_message_index and self._message_pause_seconds > 0:
                await asyncio.sleep(self._message_pause_seconds)

    async def _render_updates(self) -> None:
        while True:
            snapshot = await self._updates.get()
            if snapshot.source in {"clock", "system", "bulletins"}:
                self.query_one(f"#{snapshot.source}", Static).update(snapshot.message)
            else:
                self.query_one("#event-log", Static).update(
                    f"{snapshot.source.upper()}: {snapshot.message}"
                )
