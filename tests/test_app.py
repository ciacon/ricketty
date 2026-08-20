import asyncio
from datetime import UTC, datetime

import pytest
from textual.widgets import Static

from ricketty.app import RickettyApp
from ricketty.models import Severity, StatusSnapshot
from ricketty.providers.base import ProviderIdentity


class DashboardProvider:
    identity = ProviderIdentity(name="system", interval_seconds=60)

    async def read(self) -> StatusSnapshot:
        return StatusSnapshot(
            "system", datetime(2026, 8, 14, tzinfo=UTC), 42.5, Severity.INFO, "SYSTEM READY"
        )


class FailingDashboardProvider:
    identity = ProviderIdentity(name="system", interval_seconds=60)

    async def read(self) -> StatusSnapshot:
        raise RuntimeError("tube collapse")


@pytest.mark.asyncio
async def test_app_reveals_its_boot_message_in_the_ticker() -> None:
    app = RickettyApp(
        boot_messages=("RICKETTY READY",),
        glyph_delay_seconds=0,
        message_pause_seconds=0,
    )

    async with app.run_test() as pilot:
        await pilot.pause()

        ticker = app.query_one("#ticker", Static)
        assert str(ticker.render()) == "RICKETTY READY"


@pytest.mark.asyncio
async def test_app_reveals_each_boot_message_in_order() -> None:
    app = RickettyApp(
        boot_messages=("CHECKING TUBES", "TUBES: MOSTLY PRESENT"),
        glyph_delay_seconds=0,
        message_pause_seconds=0,
    )

    async with app.run_test() as pilot:
        await pilot.pause()

        ticker = app.query_one("#ticker", Static)
        assert str(ticker.render()) == "TUBES: MOSTLY PRESENT"


@pytest.mark.asyncio
async def test_app_holds_a_completed_message_before_showing_the_next_one() -> None:
    app = RickettyApp(
        boot_messages=("CHECKING TUBES", "TUBES: MOSTLY PRESENT"),
        glyph_delay_seconds=0,
        message_pause_seconds=60,
    )

    async with app.run_test() as pilot:
        await pilot.pause()

        ticker = app.query_one("#ticker", Static)
        assert str(ticker.render()) == "CHECKING TUBES"


@pytest.mark.asyncio
async def test_app_composes_status_panels_alongside_its_ticker() -> None:
    app = RickettyApp(boot_messages=(), glyph_delay_seconds=0, message_pause_seconds=0)

    async with app.run_test() as pilot:
        await pilot.pause()

        assert app.query_one("#clock", Static)
        assert app.query_one("#system", Static)
        assert app.query_one("#bulletins", Static)
        assert app.query_one("#event-log", Static)


@pytest.mark.asyncio
async def test_app_routes_a_provider_snapshot_to_its_panel() -> None:
    updates: asyncio.Queue[StatusSnapshot] = asyncio.Queue()
    await updates.put(
        StatusSnapshot("clock", datetime(2026, 8, 14, tzinfo=UTC), 42.5, Severity.INFO, "12:34")
    )
    app = RickettyApp(
        boot_messages=(),
        glyph_delay_seconds=0,
        message_pause_seconds=0,
        updates=updates,
        providers=(),
    )

    async with app.run_test() as pilot:
        await pilot.pause()

        assert str(app.query_one("#clock", Static).render()) == "12:34"


@pytest.mark.asyncio
async def test_app_starts_supplied_providers_and_renders_their_snapshots() -> None:
    app = RickettyApp(
        boot_messages=(),
        glyph_delay_seconds=0,
        message_pause_seconds=0,
        providers=(DashboardProvider(),),
    )

    async with app.run_test() as pilot:
        await pilot.pause()

        assert str(app.query_one("#system", Static).render()) == "SYSTEM READY"


@pytest.mark.asyncio
async def test_app_keeps_running_with_a_degraded_provider_panel() -> None:
    app = RickettyApp(
        boot_messages=(),
        glyph_delay_seconds=0,
        message_pause_seconds=0,
        providers=(FailingDashboardProvider(),),
    )

    async with app.run_test() as pilot:
        await pilot.pause()

        assert str(app.query_one("#system", Static).render()) == "PROVIDER FAILURE: tube collapse"


def test_app_exposes_control_q_and_control_c_quit_bindings() -> None:
    assert ("ctrl+q", "quit", "Quit") in RickettyApp.BINDINGS
    assert ("ctrl+c", "quit", "Quit") in RickettyApp.BINDINGS
