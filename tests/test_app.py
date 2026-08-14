import pytest
from textual.widgets import Static

from ricketty.app import RickettyApp


@pytest.mark.asyncio
async def test_app_reveals_its_boot_message_in_the_ticker() -> None:
    app = RickettyApp(boot_message="RICKETTY READY", glyph_delay_seconds=0)

    async with app.run_test() as pilot:
        await pilot.pause()

        ticker = app.query_one("#ticker", Static)
        assert str(ticker.render()) == "RICKETTY READY"
