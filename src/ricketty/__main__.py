"""Console entry point for Ricketty."""

from ricketty.app import RickettyApp


def main() -> None:
    """Run the Ricketty terminal application."""
    RickettyApp().run()


if __name__ == "__main__":
    main()
