"""The first Ricketty terminal application."""

from textual.app import App, ComposeResult
from textual.widgets import Static

from ricketty.services.typer import Ticker

DEFAULT_BOOT_MESSAGES = (
    "RICKETTY BIOS // REV 0.1",
    "PROBING TUBE INTEGRITY",
    "TUBES: MOSTLY PRESENT",
    "RICKETTY TERMINAL ONLINE",
)


class RickettyApp(App[None]):
    """A fullscreen terminal screen that slowly reveals boot text."""

    CSS_PATH = "styles.tcss"
    TITLE = "RICKETTY"

    def __init__(
        self,
        *,
        boot_messages: tuple[str, ...] = DEFAULT_BOOT_MESSAGES,
        glyph_delay_seconds: float = 0.04,
    ) -> None:
        super().__init__()
        self._boot_messages = boot_messages
        self._glyph_delay_seconds = glyph_delay_seconds

    def compose(self) -> ComposeResult:
        yield Static("", id="ticker")

    def on_mount(self) -> None:
        self.run_worker(self._reveal_boot_messages(), name="boot-messages", exclusive=True)

    async def _reveal_boot_messages(self) -> None:
        ticker = self.query_one("#ticker", Static)
        boot_ticker = Ticker(
            write=ticker.update,
            delay_seconds=self._glyph_delay_seconds,
        )
        for message in self._boot_messages:
            boot_ticker.show(message)
            await boot_ticker.wait_until_idle()
