"""Main application window for BG Remover MauL."""

from pathlib import Path
from typing import Dict, Optional
import customtkinter as ctk

from app.theme import (
    THEME,
    COLOR_BG,
    COLOR_SIDEBAR,
    COLOR_CARD,
    COLOR_ACCENT,
    COLOR_HOVER,
    COLOR_SUCCESS,
    COLOR_ERROR,
    COLOR_TEXT,
    COLOR_TEXT_SECONDARY,
    COLOR_BORDER,
)
from app.sidebar import Sidebar
from app.components.status_bar import StatusBar
from app.pages.remove_bg import RemoveBGPage
from app.pages.batch import BatchPage
from app.pages.history import HistoryPage
from app.pages.settings import SettingsPage
from app.pages.about import AboutPage
from app.core.processor import BGRemover
from app.core.settings_manager import SettingsManager
from app.core.history_manager import HistoryManager


class BGRemoverApp(ctk.CTk):
    """Main application window managing UI routing, settings, and life-cycle."""

    def __init__(self):
        """Initialize the main application window and sub-components."""
        super().__init__()

        # Load persisted settings
        self._settings = SettingsManager()

        # Window configuration
        self.title("BG Remover MauL")
        width = int(self._settings.get("window_width", 1200))
        height = int(self._settings.get("window_height", 750))
        self.geometry(f"{width}x{height}")
        self.minsize(900, 600)

        # Set Windows AppUserModelID so taskbar displays custom icon properly
        try:
            import ctypes
            myappid = "maulstudio.bgremover.desktop.1.0"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            pass

        # Load window and taskbar icon (supports normal python & PyInstaller frozen exe)
        self._set_window_icons()

        # Appearance & theme configuration
        ctk.set_appearance_mode(self._settings.theme)
        ctk.set_default_color_theme("blue")
        self.configure(fg_color=COLOR_BG)

        # Initialize core services
        self._processor = BGRemover(self._settings.ai_model)
        self._history = HistoryManager()

        # Layout configuration
        # Row 0: Status bar (top full width)
        # Row 1: Sidebar (left) | Content frame (right)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        # 1. Header Status Bar (spans columns 0 and 1)
        self._status_bar = StatusBar(self)
        self._status_bar.grid(row=0, column=0, columnspan=2, sticky="ew")

        # 2. Sidebar Navigation (left)
        self._sidebar = Sidebar(self, on_navigate=self._navigate)
        self._sidebar.grid(row=1, column=0, sticky="nsew")

        # 3. Main Content Container (right)
        self._content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._content_frame.grid(row=1, column=1, sticky="nsew", padx=12, pady=12)
        self._content_frame.grid_columnconfigure(0, weight=1)
        self._content_frame.grid_rowconfigure(0, weight=1)

        # 4. Instantiate Pages
        self._pages: Dict[str, ctk.CTkFrame] = {}
        self._create_pages()

        # 5. Default Route
        self._current_page: Optional[str] = None
        self._navigate("remove_bg")

        # 6. Window Close Intercept
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _create_pages(self) -> None:
        """Instantiate and grid all views within the content container."""
        self._pages["remove_bg"] = RemoveBGPage(
            self._content_frame,
            processor=self._processor,
            settings=self._settings,
            history_manager=self._history,
            status_bar=self._status_bar,
        )
        self._pages["batch"] = BatchPage(
            self._content_frame,
            processor=self._processor,
            settings=self._settings,
            history_manager=self._history,
            status_bar=self._status_bar,
        )
        self._pages["history"] = HistoryPage(
            self._content_frame,
            history_manager=self._history,
        )
        self._pages["settings"] = SettingsPage(
            self._content_frame,
            settings=self._settings,
            processor=self._processor,
            on_theme_change=self._on_theme_change,
        )
        self._pages["about"] = AboutPage(self._content_frame)

        for page in self._pages.values():
            page.grid(row=0, column=0, sticky="nsew")

    def _navigate(self, page_name: str) -> None:
        """Route to requested page view.
        
        Args:
            page_name: Identifier of page (e.g. 'remove_bg', 'batch', 'history', 'settings', 'about').
        """
        if self._current_page == page_name:
            return

        target_page = self._pages.get(page_name)
        if target_page is not None:
            self._current_page = page_name
            self._sidebar.set_active(page_name)
            target_page.tkraise()

            # Refresh dynamic pages when opened
            if page_name == "history" and hasattr(target_page, "refresh"):
                target_page.refresh()

    def _on_theme_change(self, theme: str) -> None:
        """Handle dynamic theme mode adjustments."""
        ctk.set_appearance_mode(theme)
        self.configure(fg_color=COLOR_BG)

    def _on_close(self) -> None:
        """Clean up active sessions and store current window geometry before exiting."""
        try:
            self._processor.close()
        except Exception:
            pass

        try:
            curr_width = max(900, self.winfo_width())
            curr_height = max(600, self.winfo_height())
            self._settings.set("window_width", curr_width)
            self._settings.set("window_height", curr_height)
        except Exception:
            pass

        self.destroy()
