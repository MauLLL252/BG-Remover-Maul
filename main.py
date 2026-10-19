"""Main entry point for BG Remover MauL desktop application."""

import sys
from pathlib import Path

# Add project root to sys.path to enable direct execution
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.app import BGRemoverApp


def main() -> None:
    """Instantiate and start the desktop application main event loop."""
    app = BGRemoverApp()
    app.mainloop()


if __name__ == "__main__":
    main()
