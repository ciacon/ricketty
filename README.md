# Ricketty

A derpy, slow-drivelling terminal information screen.

Ricketty is a Python 3.14 Textual/Rich project meant to run inside a terminal emulator such as [Cool Retro Term](https://github.com/Swordfish90/cool-retro-term). Cool Retro Term provides the CRT costume; Ricketty supplies the terminal nonsense.

## Run

```bash
uv sync
uv run ricketty
```

Ricketty is a terminal-only, offline dashboard. It reads the local clock,
Linux uptime from `/proc/uptime`, and free space on the home filesystem. It
does not make network calls, run a server, or inspect Hermes data. Press
`Ctrl-C` or `Ctrl-Q` to quit.

The dashboard works in an ordinary terminal. Cool Retro Term is optional and
only supplies the CRT presentation; see `docs/cool-retro-term.md`.

## Development

```bash
uv sync
uv run pytest
uv run ruff format --check .
uv run ruff check .
uv run pyright
```

The first v0.1 dashboard uses offline providers, a bounded asynchronous update
queue, and a deliberately slow boot ticker. See `docs/design.md` for the
runtime ownership model. Network-fed status ingestion is deliberately deferred.
