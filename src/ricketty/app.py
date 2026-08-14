"""The first Ricketty terminal application."""

from textual.app import App, ComposeResult
from textual.widgets import Static

from ricketty.services.typer import reveal


class RickettyApp(App[None]):
    """A fullscreen terminal screen that slowly reveals boot text."""

    CSS_PATH = "styles.tcss"
    TITLE = "RICKETTY"

    def __init__(
        self,
        *,
        boot_message: str = "RICKETTY TERMINAL ONLINE",
        glyph_delay_seconds: float = 0.04,
    ) -> None:
        super().__init__()
        self._boot_message = boot_message
        self._glyph_delay_seconds = glyph_delay_seconds

    def compose(self) -> ComposeResult:
        yield Static("", id="ticker")

    def on_mount(self) -> None:
        self.run_worker(self._reveal_boot_message(), name="boot-message", exclusive=True)

    async def _reveal_boot_message(self) -> None:
        ticker = self.query_one("#ticker", Static)
        await reveal(
            self._boot_message,
            write=ticker.update,
            delay_seconds=self._glyph_delay_seconds,
        )
