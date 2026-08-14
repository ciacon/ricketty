# Ricketty

A derpy, slow-drivelling terminal information screen.

Ricketty is a Python 3.14 Textual/Rich project meant to run inside a terminal emulator such as [Cool Retro Term](https://github.com/Swordfish90/cool-retro-term). Cool Retro Term provides the CRT costume; Ricketty supplies the terminal nonsense.

## Development

```bash
uv sync
uv run pytest
uv run ruff format --check .
uv run ruff check .
uv run pyright
```

The first vertical slice deliberately concentrates on cancellable, slow ticker output. Dashboard panels and network-fed status ingestion arrive later.
