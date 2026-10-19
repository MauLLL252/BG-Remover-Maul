"""Single item in the batch processing queue displaying thumbnail, filename, and status."""

from pathlib import Path
from typing import Callable, Optional
import customtkinter as ctk
from PIL import Image

from app.core.worker import TaskStatus
from app.theme import (
    COLOR_CARD,
    COLOR_TEXT,
    COLOR_TEXT_SECONDARY,
    COLOR_BORDER,
    COLOR_ACCENT,
    COLOR_SUCCESS,
    COLOR_ERROR,
)
from app.utils.image_utils import create_thumbnail, get_file_size_str


class QueueItem(ctk.CTkFrame):
    """Widget representing one queued image in the batch list."""

    def __init__(
        self,
        parent,
        file_path: Path,
        task_id: int,
        on_remove: Optional[Callable[[int], None]] = None,
        **kwargs,
    ):
        """Initialize a queue item row.
        
        Args:
            parent: Parent container (e.g. CTkScrollableFrame).
            file_path: Path to the target image file.
            task_id: Unique identifier for this task in the batch queue.
            on_remove: Callback invoked with task_id when remove button is clicked.
            **kwargs: Extra arguments passed to CTkFrame.
        """
        super().__init__(
            parent,
            height=60,
            fg_color=COLOR_CARD,
            corner_radius=8,
            border_width=1,
            border_color=COLOR_BORDER,
            **kwargs,
        )
        self.grid_propagate(False)

        self._file_path = Path(file_path)
        self._task_id = task_id
        self._on_remove = on_remove
        self._thumb_image: Optional[ctk.CTkImage] = None

        # Setup column layouts
        self.grid_columnconfigure(0, weight=0)  # Thumbnail
        self.grid_columnconfigure(1, weight=1)  # File details
        self.grid_columnconfigure(2, weight=0)  # Status badge
        self.grid_columnconfigure(3, weight=0)  # Remove button
        self.grid_rowconfigure(0, weight=1)

        # 1. Thumbnail
        self._create_thumbnail_widget()

        # 2. Filename & Size Info
        self._info_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._info_frame.grid(row=0, column=1, sticky="w", padx=(10, 10))

        # Truncate filename if unusually long
        display_name = self._file_path.name
        if len(display_name) > 35:
            display_name = display_name[:32] + "..."

        self._name_label = ctk.CTkLabel(
            self._info_frame,
            text=display_name,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=COLOR_TEXT,
            anchor="w",
        )
        self._name_label.pack(anchor="w")

        size_text = get_file_size_str(self._file_path)
        self._sub_label = ctk.CTkLabel(
            self._info_frame,
            text=f"Size: {size_text}",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=COLOR_TEXT_SECONDARY,
            anchor="w",
        )
        self._sub_label.pack(anchor="w")

        # 3. Status Badge
        self._status_badge = ctk.CTkLabel(
            self,
            text="Waiting",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color=("#e2e8f0", "#334155"),
            text_color=COLOR_TEXT_SECONDARY,
            corner_radius=6,
            padx=10,
            pady=4,
        )
        self._status_badge.grid(row=0, column=2, padx=(10, 10), sticky="e")

        # 4. Remove Button
        self._remove_btn = ctk.CTkButton(
            self,
            text="✕",
            width=28,
            height=28,
            corner_radius=6,
            fg_color="transparent",
            hover_color=COLOR_ERROR,
            text_color=COLOR_TEXT_SECONDARY,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            command=self._handle_remove,
        )
        self._remove_btn.grid(row=0, column=3, padx=(0, 10), sticky="e")

    def _create_thumbnail_widget(self) -> None:
        """Load and display a 40x40 thumbnail image."""
        try:
            with Image.open(self._file_path) as img:
                thumb = create_thumbnail(img, (40, 40))
                # Convert to RGB/RGBA if necessary
                if thumb.mode not in ("RGB", "RGBA"):
                    thumb = thumb.convert("RGBA")
                self._thumb_image = ctk.CTkImage(
                    light_image=thumb,
                    dark_image=thumb,
                    size=(thumb.width, thumb.height),
                )
            self._thumb_label = ctk.CTkLabel(
                self,
                text="",
                image=self._thumb_image,
                width=44,
                height=44,
            )
        except Exception:
            self._thumb_label = ctk.CTkLabel(
                self,
                text="🖼",
                font=ctk.CTkFont(size=18),
                width=44,
                height=44,
            )
        self._thumb_label.grid(row=0, column=0, padx=(10, 0), sticky="w")

    def update_status(self, status: TaskStatus, error_msg: str = "") -> None:
        """Update the status badge text, color, and optional error message.
        
        Args:
            status: New TaskStatus enum value.
            error_msg: Optional error description if status is FAILED.
        """
        if status == TaskStatus.WAITING:
            self._status_badge.configure(
                text="Waiting",
                fg_color=("#e2e8f0", "#334155"),
                text_color=COLOR_TEXT_SECONDARY,
            )
            self._remove_btn.configure(state="normal")
        elif status == TaskStatus.PROCESSING:
            self._status_badge.configure(
                text="Processing...",
                fg_color=COLOR_ACCENT,
                text_color=("#ffffff", "#ffffff"),
            )
            self._remove_btn.configure(state="disabled")
        elif status == TaskStatus.COMPLETED:
            self._status_badge.configure(
                text="✓ Completed",
                fg_color=COLOR_SUCCESS,
                text_color=("#ffffff", "#ffffff"),
            )
            self._remove_btn.configure(state="normal")
        elif status == TaskStatus.FAILED:
            display_err = f"✕ Failed: {error_msg}" if error_msg else "✕ Failed"
            if len(display_err) > 30:
                display_err = display_err[:27] + "..."
            self._status_badge.configure(
                text=display_err,
                fg_color=COLOR_ERROR,
                text_color=("#ffffff", "#ffffff"),
            )
            self._sub_label.configure(
                text=f"Error: {error_msg[:40]}..." if len(error_msg) > 40 else f"Error: {error_msg}",
                text_color=COLOR_ERROR,
            )
            self._remove_btn.configure(state="normal")
        elif status == TaskStatus.CANCELLED:
            self._status_badge.configure(
                text="Cancelled",
                fg_color=("#94a3b8", "#475569"),
                text_color=("#ffffff", "#ffffff"),
            )
            self._remove_btn.configure(state="normal")

    def _handle_remove(self) -> None:
        """Invoke removal callback."""
        if self._on_remove is not None:
            self._on_remove(self._task_id)

    @property
    def task_id(self) -> int:
        """Unique task ID for this queue item."""
        return self._task_id

    @property
    def file_path(self) -> Path:
        """Path to the image file."""
        return self._file_path
