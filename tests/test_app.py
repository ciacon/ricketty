import pytest
from textual.widgets import Static

from ricketty.app import RickettyApp


@pytest.mark.asyncio
async def test_app_reveals_its_boot_message_in_the_ticker() -> None:
    app = RickettyApp(boot_messages=("RICKETTY READY",), glyph_delay_seconds=0)

    async with app.run_test() as pilot:
        await pilot.pause()

        ticker = app.query_one("#ticker", Static)
        assert str(ticker.render()) == "RICKETTY READY"


@pytest.mark.asyncio
async def test_app_reveals_each_boot_message_in_order() -> None:
    app = RickettyApp(
        boot_messages=("CHECKING TUBES", "TUBES: MOSTLY PRESENT"), glyph_delay_seconds=0
    )

    async with app.run_test() as pilot:
        await pilot.pause()

        ticker = app.query_one("#ticker", Static)
        assert str(ticker.render()) == "TUBES: MOSTLY PRESENT"
