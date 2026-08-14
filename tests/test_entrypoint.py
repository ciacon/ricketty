from pytest import MonkeyPatch

import ricketty.__main__ as entrypoint


def test_main_runs_the_ricketty_app(monkeypatch: MonkeyPatch) -> None:
    calls: list[str] = []

    class FakeApp:
        def run(self) -> None:
            calls.append("run")

    monkeypatch.setattr(entrypoint, "RickettyApp", FakeApp)

    entrypoint.main()

    assert calls == ["run"]
