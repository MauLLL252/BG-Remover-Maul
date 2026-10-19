"""Processing history page displaying past operations and file shortcuts."""

import os
from pathlib import Path
import subprocess
from tkinter import messagebox
from typing import List, Dict, Any
import customtkinter as ctk

from app.theme import (
    COLOR_CARD,
    COLOR_BORDER,
    COLOR_TEXT,
    COLOR_TEXT_SECONDARY,
    COLOR_ACCENT,
    COLOR_HOVER,
    COLOR_SUCCESS,
    COLOR_ERROR,
)


class HistoryPage(ctk.CTkFrame):
    """Page listing history records of processed images with direct file explorer links."""

    def __init__(self, parent, history_manager, **kwargs):
        """Initialize HistoryPage.
        
        Args:
            parent: Parent container.
            history_manager: HistoryManager instance.
            **kwargs: Extra arguments passed to CTkFrame.
        """
        super().__init__(parent, fg_color="transparent", **kwargs)
        self._history = history_manager
        self._entry_widgets: List[ctk.CTkFrame] = []

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Create header controls and scrollable history container."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # 1. Header Bar
        self._header_frame = ctk.CTkFrame(
            self,
            fg_color=COLOR_CARD,
            corner_radius=10,
            border_width=1,
            border_color=COLOR_BORDER,
            height=54,
        )
        self._header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 10))
        self._header_frame.grid_propagate(False)
        self._header_frame.grid_columnconfigure(0, weight=1)
        self._header_frame.grid_rowconfigure(0, weight=1)

        self._title_label = ctk.CTkLabel(
            self._header_frame,
            text="📋   Processing History",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color=COLOR_TEXT,
        )
        self._title_label.grid(row=0, column=0, sticky="w", padx=16, pady=8)

        self._clear_btn = ctk.CTkButton(
            self._header_frame,
            text="🗑  Clear History",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            fg_color="transparent",
            border_width=1,
            border_color=COLOR_BORDER,
            text_color=COLOR_TEXT_SECONDARY,
            hover_color=COLOR_ERROR,
            height=34,
            corner_radius=8,
            command=self._clear_history,
        )
        self._clear_btn.grid(row=0, column=1, sticky="e", padx=16, pady=8)

        # 2. Scrollable History List
        self._scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=COLOR_CARD,
            corner_radius=10,
            border_width=1,
            border_color=COLOR_BORDER,
        )
        self._scroll_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        self._scroll_frame.grid_columnconfigure(0, weight=1)

        self._empty_label = ctk.CTkLabel(
            self._scroll_frame,
            text="📋\n\nNo processing history yet\nImages you process will be logged here.",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLOR_TEXT_SECONDARY,
            justify="center",
        )

        self.refresh()

    def refresh(self) -> None:
        """Reload and redisplay history entries. Called when page becomes visible."""
        # Clean up existing widgets
        for widget in self._entry_widgets:
            widget.destroy()
        self._entry_widgets.clear()

        entries: List[Dict[str, Any]] = self._history.get_entries()

        if not entries:
            self._empty_label.pack(pady=80)
            self._clear_btn.configure(state="disabled")
            return

        self._empty_label.pack_forget()
        self._clear_btn.configure(state="normal")

        for entry in entries:
            item_card = self._create_history_row(entry)
            item_card.pack(fill="x", padx=8, pady=5)
            self._entry_widgets.append(item_card)

    def _create_history_row(self, entry: Dict[str, Any]) -> ctk.CTkFrame:
        """Generate a structured card widget for one history log entry."""
        card = ctk.CTkFrame(
            self._scroll_frame,
            fg_color=("#f8fafc", "#1e293b"),
            corner_radius=8,
            border_width=1,
            border_color=COLOR_BORDER,
        )
        card.grid_columnconfigure(0, weight=1)
        card.grid_columnconfigure(1, weight=0)

        raw_time = entry.get('timestamp', '')
        time_display = raw_time.replace('T', ' ')[:19] if raw_time else 'Unknown time'
        input_file = entry.get('input_file', '')
        output_file = entry.get('output_file', '')
        model_name = entry.get('model', 'u2net')
        status = entry.get('status', 'Completed')

        input_name = Path(input_file).name if input_file else 'Unknown'
        out_path = Path(output_file) if output_file else None
        has_output_file = bool(out_path and out_path.exists())

        # Left Info Stack
        left_frame = ctk.CTkFrame(card, fg_color="transparent")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=12, pady=10)

        # Row 1: Timestamp & Model badge
        header_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        header_frame.pack(anchor="w", fill="x")

        time_label = ctk.CTkLabel(
            header_frame,
            text=time_display,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=COLOR_TEXT_SECONDARY,
        )
        time_label.pack(side="left")

        model_badge = ctk.CTkLabel(
            header_frame,
            text=f"Model: {model_name}",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            fg_color=("#e2e8f0", "#334155"),
            text_color=COLOR_TEXT,
            corner_radius=4,
            padx=6,
            pady=1,
        )
        model_badge.pack(side="left", padx=(10, 0))

        # Row 2: Filename
        name_label = ctk.CTkLabel(
            left_frame,
            text=f"File: {input_name}",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=COLOR_TEXT,
            anchor="w",
        )
        name_label.pack(anchor="w", pady=(3, 1))

        # Row 3: Output path / status
        if output_file:
            path_display = f"Saved: {out_path.name if out_path else output_file}"
        else:
            path_display = "Processed (preview only, not saved to disk)"

        sub_label = ctk.CTkLabel(
            left_frame,
            text=path_display,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=COLOR_TEXT_SECONDARY,
            anchor="w",
        )
        sub_label.pack(anchor="w")

        # Right Action & Status Stack
        right_frame = ctk.CTkFrame(card, fg_color="transparent")
        right_frame.grid(row=0, column=1, sticky="e", padx=12, pady=10)

        # Status badge
        is_success = "Completed" in status
        badge_fg = COLOR_SUCCESS if is_success else COLOR_ERROR
        badge_text = "✓ Completed" if is_success else "✕ Failed"

        status_badge = ctk.CTkLabel(
            right_frame,
            text=badge_text,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color=badge_fg,
            text_color=("#ffffff", "#ffffff"),
            corner_radius=6,
            padx=8,
            pady=3,
        )
        status_badge.pack(anchor="e", pady=(0, 6))

        # Explorer Buttons
        btn_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        btn_frame.pack(anchor="e")

        if has_output_file:
            open_file_btn = ctk.CTkButton(
                btn_frame,
                text="📂 View",
                font=ctk.CTkFont(family="Segoe UI", size=11),
                fg_color=COLOR_ACCENT,
                hover_color=COLOR_HOVER,
                text_color=("#ffffff", "#ffffff"),
                width=65,
                height=26,
                corner_radius=6,
                command=lambda p=output_file: self._open_file(p),
            )
            open_file_btn.pack(side="left", padx=(0, 5))

            open_dir_btn = ctk.CTkButton(
                btn_frame,
                text="📁 Folder",
                font=ctk.CTkFont(family="Segoe UI", size=11),
                fg_color="transparent",
                border_width=1,
                border_color=COLOR_BORDER,
                text_color=COLOR_TEXT,
                hover_color=("#cbd5e1", "#334155"),
                width=65,
                height=26,
                corner_radius=6,
                command=lambda p=out_path.parent: self._open_folder(p),
            )
            open_dir_btn.pack(side="left")

        return card

    def _clear_history(self) -> None:
        """Confirm and clear all stored processing history."""
        if not self._history.get_entries():
            return

        confirm = messagebox.askyesno(
            "Clear History",
            "Are you sure you want to permanently clear the processing history?",
        )
        if confirm:
            self._history.clear()
            self.refresh()

    def _open_file(self, file_path_str: str) -> None:
        """Open the target file in Windows Explorer with file selected."""
        path = Path(file_path_str)
        if path.exists():
            try:
                subprocess.Popen(["explorer", f"/select,{str(path.resolve())}"])
            except Exception as exc:
                messagebox.showerror("Error", f"Failed to open explorer:\n{exc}")
        else:
            messagebox.showwarning("File Missing", f"File does not exist:\n{file_path_str}")

    def _open_folder(self, folder_path: Path) -> None:
        """Open containing folder in Windows Explorer."""
        if folder_path.exists() and folder_path.is_dir():
            try:
                subprocess.Popen(["explorer", str(folder_path.resolve())])
            except Exception as exc:
                messagebox.showerror("Error", f"Failed to open folder:\n{exc}")
        else:
            messagebox.showwarning("Folder Missing", f"Folder does not exist:\n{folder_path}")
