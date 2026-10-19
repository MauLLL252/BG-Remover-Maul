"""Application settings page for preferences and AI model management."""

from pathlib import Path
import subprocess
from tkinter import filedialog, messagebox
from typing import Callable
import customtkinter as ctk

from app.core.settings_manager import AVAILABLE_MODELS
from app.theme import (
    COLOR_CARD,
    COLOR_BORDER,
    COLOR_TEXT,
    COLOR_TEXT_SECONDARY,
    COLOR_ACCENT,
    COLOR_HOVER,
    COLOR_SUCCESS,
)
from app.utils.file_utils import get_app_data_dir


class SettingsPage(ctk.CTkFrame):
    """Settings view allowing user to configure directories, themes, and AI models."""

    def __init__(
        self,
        parent,
        settings,
        processor,
        on_theme_change: Callable[[str], None],
        **kwargs,
    ):
        """Initialize SettingsPage.
        
        Args:
            parent: Parent container.
            settings: SettingsManager instance.
            processor: BGRemover instance.
            on_theme_change: Callback when theme is toggled.
            **kwargs: Extra arguments passed to CTkFrame.
        """
        super().__init__(parent, fg_color="transparent", **kwargs)

        self._settings = settings
        self._processor = processor
        self._on_theme_change = on_theme_change

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Construct scrollable settings layout with distinct card sections."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self._scroll.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self._scroll.grid_columnconfigure(0, weight=1)

        # Header Title
        title_label = ctk.CTkLabel(
            self._scroll,
            text="Settings & Preferences",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=COLOR_TEXT,
            anchor="w",
        )
        title_label.pack(fill="x", padx=4, pady=(5, 15))

        # --- Section 1: Output Directory ---
        self._create_output_section()

        # --- Section 2: Appearance & Theme ---
        self._create_appearance_section()

        # --- Section 3: AI Model ---
        self._create_model_section()

        # --- Section 4: Data & Storage ---
        self._create_storage_section()

    def _create_output_section(self) -> None:
        """Section for default export folder."""
        card = self._create_card("📁   Default Output Directory")

        desc_label = ctk.CTkLabel(
            card,
            text="Choose where processed transparent images should be saved by default.",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLOR_TEXT_SECONDARY,
            anchor="w",
        )
        desc_label.pack(fill="x", padx=16, pady=(0, 10))

        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=(0, 14))

        curr_dir = self._settings.output_directory
        display_dir = curr_dir if curr_dir else "Same folder as original image (default)"

        self._dir_label = ctk.CTkLabel(
            row,
            text=display_dir,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLOR_TEXT,
            fg_color=("#e2e8f0", "#1e293b"),
            corner_radius=6,
            height=36,
            padx=12,
            anchor="w",
        )
        self._dir_label.pack(side="left", fill="x", expand=True, padx=(0, 10))

        browse_btn = ctk.CTkButton(
            row,
            text="Browse...",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_HOVER,
            width=90,
            height=36,
            corner_radius=6,
            command=self._browse_output_folder,
        )
        browse_btn.pack(side="right")

        if curr_dir:
            reset_btn = ctk.CTkButton(
                row,
                text="Reset",
                font=ctk.CTkFont(family="Segoe UI", size=12),
                fg_color="transparent",
                border_width=1,
                border_color=COLOR_BORDER,
                text_color=COLOR_TEXT_SECONDARY,
                hover_color=("#cbd5e1", "#334155"),
                width=70,
                height=36,
                corner_radius=6,
                command=self._reset_output_folder,
            )
            reset_btn.pack(side="right", padx=(0, 6))

    def _create_appearance_section(self) -> None:
        """Section for UI theme selection."""
        card = self._create_card("🎨   Appearance & Theme")

        desc_label = ctk.CTkLabel(
            card,
            text="Customize the look and feel with Dark or Light mode.",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLOR_TEXT_SECONDARY,
            anchor="w",
        )
        desc_label.pack(fill="x", padx=16, pady=(0, 10))

        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=(0, 14))

        theme_label = ctk.CTkLabel(
            row,
            text="Theme Mode:",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=COLOR_TEXT,
        )
        theme_label.pack(side="left")

        current_theme = self._settings.theme.capitalize()
        self._theme_seg = ctk.CTkSegmentedButton(
            row,
            values=["Dark", "Light"],
            font=ctk.CTkFont(family="Segoe UI", size=12),
            selected_color=COLOR_ACCENT,
            selected_hover_color=COLOR_HOVER,
            command=self._change_theme,
        )
        self._theme_seg.set(current_theme)
        self._theme_seg.pack(side="right")

    def _create_model_section(self) -> None:
        """Section for AI model configuration."""
        card = self._create_card("🧠   AI Model Selection")

        desc_label = ctk.CTkLabel(
            card,
            text="Select which neural network model rembg should utilize for inference.",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLOR_TEXT_SECONDARY,
            anchor="w",
        )
        desc_label.pack(fill="x", padx=16, pady=(0, 10))

        # Model Selector Dropdown
        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=(0, 10))

        model_label = ctk.CTkLabel(
            row,
            text="Active Model:",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=COLOR_TEXT,
        )
        model_label.pack(side="left")

        model_keys = list(AVAILABLE_MODELS.keys())
        current_model = self._settings.ai_model
        if current_model not in model_keys:
            current_model = model_keys[0]

        self._model_opt = ctk.CTkOptionMenu(
            row,
            values=model_keys,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            fg_color=COLOR_ACCENT,
            button_color=COLOR_ACCENT,
            button_hover_color=COLOR_HOVER,
            width=200,
            command=self._change_model,
        )
        self._model_opt.set(current_model)
        self._model_opt.pack(side="right")

        # Model Details Panel
        self._model_details_frame = ctk.CTkFrame(
            card,
            fg_color=("#e2e8f0", "#1e293b"),
            corner_radius=8,
            border_width=1,
            border_color=COLOR_BORDER,
        )
        self._model_details_frame.pack(fill="x", padx=16, pady=(0, 14))

        self._model_name_label = ctk.CTkLabel(
            self._model_details_frame,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=COLOR_TEXT,
            anchor="w",
        )
        self._model_name_label.pack(fill="x", padx=12, pady=(10, 2))

        self._model_desc_label = ctk.CTkLabel(
            self._model_details_frame,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLOR_TEXT_SECONDARY,
            anchor="w",
        )
        self._model_desc_label.pack(fill="x", padx=12, pady=(0, 6))

        self._model_status_label = ctk.CTkLabel(
            self._model_details_frame,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            anchor="w",
        )
        self._model_status_label.pack(fill="x", padx=12, pady=(0, 10))

        self._update_model_info(current_model)

    def _create_storage_section(self) -> None:
        """Section showing local app data and cache paths."""
        card = self._create_card("💾   Storage & Application Data")

        desc_label = ctk.CTkLabel(
            card,
            text="Settings and processing history are saved locally on this machine.",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLOR_TEXT_SECONDARY,
            anchor="w",
        )
        desc_label.pack(fill="x", padx=16, pady=(0, 10))

        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=(0, 14))

        app_data_path = get_app_data_dir()
        path_label = ctk.CTkLabel(
            row,
            text=f"Location: {app_data_path}",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=COLOR_TEXT_SECONDARY,
            anchor="w",
        )
        path_label.pack(side="left", fill="x", expand=True)

        open_data_btn = ctk.CTkButton(
            row,
            text="Open Folder",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            fg_color="transparent",
            border_width=1,
            border_color=COLOR_BORDER,
            text_color=COLOR_TEXT,
            hover_color=("#cbd5e1", "#334155"),
            width=100,
            height=34,
            corner_radius=6,
            command=lambda: self._open_dir(app_data_path),
        )
        open_data_btn.pack(side="right")

    def _create_card(self, title: str) -> ctk.CTkFrame:
        """Helper to create standard rounded settings card."""
        card = ctk.CTkFrame(
            self._scroll,
            fg_color=COLOR_CARD,
            corner_radius=10,
            border_width=1,
            border_color=COLOR_BORDER,
        )
        card.pack(fill="x", padx=4, pady=(0, 14))

        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLOR_TEXT,
            anchor="w",
        )
        title_label.pack(fill="x", padx=16, pady=(14, 4))
        return card

    def _browse_output_folder(self) -> None:
        """Open folder dialog to set default output directory."""
        initial = self._settings.output_directory or str(Path.home())
        chosen = filedialog.askdirectory(
            title="Select Default Output Directory", initialdir=initial
        )
        if chosen:
            self._settings.output_directory = chosen
            self._dir_label.configure(text=chosen)

    def _reset_output_folder(self) -> None:
        """Reset output directory to default."""
        self._settings.output_directory = ""
        self._dir_label.configure(text="Same folder as original image (default)")

    def _change_theme(self, theme_choice: str) -> None:
        """Change application appearance mode."""
        theme_str = theme_choice.lower()
        self._settings.theme = theme_str
        ctk.set_appearance_mode(theme_str)
        if self._on_theme_change:
            self._on_theme_change(theme_str)

    def _change_model(self, model_key: str) -> None:
        """Change the active AI model."""
        self._settings.ai_model = model_key
        self._processor.change_model(model_key)
        self._update_model_info(model_key)

    def _update_model_info(self, model_key: str) -> None:
        """Update description and readiness badge for selected model."""
        info = AVAILABLE_MODELS.get(model_key, {})
        name = info.get("name", model_key)
        desc = info.get("description", "AI model for background removal")
        license_str = info.get("license", "Apache 2.0")

        self._model_name_label.configure(text=f"{name}  ({license_str})")
        self._model_desc_label.configure(text=desc)

        is_ready = self._processor.is_model_ready()
        if is_ready:
            self._model_status_label.configure(
                text="✓ Model cached and ready for instant inference",
                text_color=COLOR_SUCCESS,
            )
        else:
            self._model_status_label.configure(
                text="ℹ Model not yet downloaded. Will be downloaded automatically on first use (~176 MB).",
                text_color=COLOR_ACCENT,
            )

    def _open_dir(self, directory: Path) -> None:
        """Open specified directory in Windows Explorer."""
        if directory.exists():
            try:
                subprocess.Popen(["explorer", str(directory.resolve())])
            except Exception as exc:
                messagebox.showerror("Error", f"Failed to open directory:\n{exc}")
