"""Header status bar widget showing app branding and execution status."""

import customtkinter as ctk
from app.theme import (
    COLOR_SIDEBAR,
    COLOR_TEXT,
    COLOR_TEXT_SECONDARY,
    COLOR_ACCENT,
    COLOR_SUCCESS,
    COLOR_ERROR,
    COLOR_BORDER,
)


class StatusBar(ctk.CTkFrame):
    """Header bar widget displaying app title, subtitle, and dynamic status."""

    def __init__(self, parent, **kwargs):
        """Initialize the status bar.
        
        Args:
            parent: Parent widget.
            **kwargs: Extra arguments passed to CTkFrame.
        """
        super().__init__(
            parent,
            height=50,
            corner_radius=0,
            fg_color=COLOR_SIDEBAR,
            border_width=1,
            border_color=COLOR_BORDER,
            **kwargs,
        )
        self.grid_propagate(False)

        # Configure layout: Column 0 for logo/title, Column 1 stretches for status
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Left branding container
        self._brand_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._brand_frame.grid(row=0, column=0, sticky="w", padx=(20, 10), pady=5)

        self._title_label = ctk.CTkLabel(
            self._brand_frame,
            text="✨ BG Remover",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=COLOR_TEXT,
        )
        self._title_label.pack(side="left", padx=(0, 6))

        self._author_badge = ctk.CTkLabel(
            self._brand_frame,
            text="MauL",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color=COLOR_ACCENT,
            text_color=("#ffffff", "#ffffff"),
            corner_radius=6,
            padx=7,
            pady=2,
        )
        self._author_badge.pack(side="left")

        # Right status container
        self._status_label = ctk.CTkLabel(
            self,
            text="Ready",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLOR_TEXT_SECONDARY,
            anchor="e",
        )
        self._status_label.grid(row=0, column=1, sticky="e", padx=(10, 20), pady=5)

    def set_status(self, text: str, status_type: str = "info") -> None:
        """Update the displayed status text and color.
        
        Args:
            text: Status message to display.
            status_type: One of 'info', 'processing', 'success', 'error'.
        """
        status_colors = {
            "info": COLOR_TEXT_SECONDARY,
            "processing": COLOR_ACCENT,
            "success": COLOR_SUCCESS,
            "error": COLOR_ERROR,
        }
        chosen_color = status_colors.get(status_type, COLOR_TEXT_SECONDARY)

        prefix_icons = {
            "info": "ℹ ",
            "processing": "⏳ ",
            "success": "✓ ",
            "error": "✕ ",
        }
        # Avoid double prefixes if text already includes an icon
        icon = prefix_icons.get(status_type, "")
        display_text = text if any(text.startswith(ic.strip()) for ic in prefix_icons.values()) else f"{icon}{text}"

        self._status_label.configure(text=display_text, text_color=chosen_color)

    def set_processing(self, current: int, total: int) -> None:
        """Display processing progress.
        
        Args:
            current: Current item index (1-based).
            total: Total number of items in batch.
        """
        self.set_status(f"Processing {current}/{total}...", status_type="processing")
