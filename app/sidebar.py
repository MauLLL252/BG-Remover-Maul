"""Left sidebar navigation component for BG Remover MauL."""

from typing import Callable, Dict
import customtkinter as ctk

from app.theme import (
    COLOR_SIDEBAR,
    COLOR_BORDER,
    COLOR_TEXT,
    COLOR_TEXT_SECONDARY,
    COLOR_ACCENT,
    COLOR_HOVER,
)


class Sidebar(ctk.CTkFrame):
    """Sidebar navigation panel containing page routing buttons and branding."""

    NAV_ITEMS = [
        ('remove_bg', '🖼   Remove Background'),
        ('batch', '📦   Batch Processing'),
        ('history', '📋   History'),
        ('settings', '⚙   Settings'),
        ('about', 'ℹ   About'),
    ]

    def __init__(self, parent, on_navigate: Callable[[str], None], **kwargs):
        """Initialize the sidebar.
        
        Args:
            parent: Parent container widget.
            on_navigate: Callback invoked with page key (e.g. 'remove_bg') when button clicked.
            **kwargs: Extra arguments passed to CTkFrame.
        """
        super().__init__(
            parent,
            width=220,
            corner_radius=0,
            fg_color=COLOR_SIDEBAR,
            border_width=1,
            border_color=COLOR_BORDER,
            **kwargs,
        )
        self.grid_propagate(False)

        self._on_navigate = on_navigate
        self._buttons: Dict[str, ctk.CTkButton] = {}
        self._active_page = ''

        # Grid configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)  # Space between nav and footer

        # 1. Branding Header
        self._header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._header_frame.grid(row=0, column=0, sticky="ew", padx=16, pady=(20, 10))

        self._title_label = ctk.CTkLabel(
            self._header_frame,
            text="BG Remover",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=COLOR_TEXT,
        )
        self._title_label.pack(anchor="w")

        self._sub_frame = ctk.CTkFrame(self._header_frame, fg_color="transparent")
        self._sub_frame.pack(anchor="w", pady=(3, 0))

        self._sub_label = ctk.CTkLabel(
            self._sub_frame,
            text="by MauL Studio",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=COLOR_TEXT_SECONDARY,
        )
        self._sub_label.pack(side="left")

        # Separator line
        self._sep = ctk.CTkFrame(self, height=1, fg_color=COLOR_BORDER)
        self._sep.grid(row=1, column=0, sticky="ew", padx=12, pady=(10, 15))

        # 2. Navigation Buttons Container
        self._nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._nav_frame.grid(row=2, column=0, sticky="new", padx=10, pady=0)

        for page_key, display_text in self.NAV_ITEMS:
            btn = ctk.CTkButton(
                self._nav_frame,
                text=display_text,
                anchor="w",
                height=42,
                corner_radius=8,
                fg_color="transparent",
                hover_color=("#cbd5e1", "#334155"),
                text_color=COLOR_TEXT,
                font=ctk.CTkFont(family="Segoe UI", size=13, weight="normal"),
                command=lambda pk=page_key: self._handle_click(pk),
            )
            btn.pack(fill="x", pady=4)
            self._buttons[page_key] = btn

        # 3. Footer Container
        self._footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._footer_frame.grid(row=3, column=0, sticky="sew", padx=16, pady=(10, 15))

        self._version_label = ctk.CTkLabel(
            self._footer_frame,
            text="v1.0.0",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=COLOR_TEXT_SECONDARY,
            anchor="w",
        )
        self._version_label.pack(anchor="w")

    def _handle_click(self, page_name: str) -> None:
        """Handle button click and invoke navigation callback."""
        if self._on_navigate is not None:
            self._on_navigate(page_name)

    def set_active(self, page_name: str) -> None:
        """Highlight active navigation button and reset others.
        
        Args:
            page_name: Key of the active page (e.g. 'remove_bg').
        """
        self._active_page = page_name
        for key, btn in self._buttons.items():
            if key == page_name:
                btn.configure(
                    fg_color=COLOR_ACCENT,
                    hover_color=COLOR_HOVER,
                    text_color=("#ffffff", "#ffffff"),
                    font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    hover_color=("#cbd5e1", "#334155"),
                    text_color=COLOR_TEXT,
                    font=ctk.CTkFont(family="Segoe UI", size=13, weight="normal"),
                )
