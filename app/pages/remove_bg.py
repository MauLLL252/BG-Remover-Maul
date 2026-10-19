"""Single image background removal page."""

from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Optional
import customtkinter as ctk
from PIL import Image

from app.components.image_preview import ImagePreview
from app.core.worker import ProcessingWorker, ProcessingTask, TaskStatus
from app.theme import (
    COLOR_CARD,
    COLOR_BORDER,
    COLOR_TEXT,
    COLOR_TEXT_SECONDARY,
    COLOR_ACCENT,
    COLOR_HOVER,
    COLOR_SUCCESS,
)
from app.utils.image_utils import validate_image, get_image_info
from app.utils.file_utils import get_output_filename, get_unique_filepath


class RemoveBGPage(ctk.CTkFrame):
    """Main page for processing a single image with live preview and export."""

    def __init__(self, parent, processor, settings, history_manager, status_bar, **kwargs):
        """Initialize RemoveBGPage.
        
        Args:
            parent: Parent container.
            processor: BGRemover instance.
            settings: SettingsManager instance.
            history_manager: HistoryManager instance.
            status_bar: StatusBar instance.
            **kwargs: Extra arguments passed to CTkFrame.
        """
        super().__init__(parent, fg_color="transparent", **kwargs)

        self._processor = processor
        self._settings = settings
        self._history = history_manager
        self._status_bar = status_bar

        self._current_image_path: Optional[Path] = None
        self._original_pil: Optional[Image.Image] = None
        self._result_image: Optional[Image.Image] = None
        self._worker: Optional[ProcessingWorker] = None

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Construct the layout with upload section, preview panels, and actions."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)  # Preview panel expands

        # 1. Top Section: Upload / File Info Area
        self._upload_frame = ctk.CTkFrame(
            self,
            fg_color=COLOR_CARD,
            corner_radius=10,
            border_width=1,
            border_color=COLOR_BORDER,
        )
        self._upload_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 10))
        self._upload_frame.grid_columnconfigure(0, weight=1)

        self._upload_inner = ctk.CTkFrame(self._upload_frame, fg_color="transparent")
        self._upload_inner.pack(fill="x", padx=16, pady=12)

        self._upload_label = ctk.CTkLabel(
            self._upload_inner,
            text="Upload an image to remove background (Supports JPG, PNG, WEBP)",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLOR_TEXT_SECONDARY,
            anchor="w",
        )
        self._upload_label.pack(side="left", fill="x", expand=True)

        self._select_btn = ctk.CTkButton(
            self._upload_inner,
            text="📁  Select Image",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_HOVER,
            height=36,
            corner_radius=8,
            command=self._select_image,
        )
        self._select_btn.pack(side="right", padx=(10, 0))

        # 2. Middle Section: Side-by-side Image Preview
        self._preview = ImagePreview(self)
        self._preview.grid(row=1, column=0, sticky="nsew", padx=0, pady=(0, 10))

        # 3. Bottom Section: Action Controls
        self._actions_frame = ctk.CTkFrame(
            self,
            fg_color=COLOR_CARD,
            corner_radius=10,
            border_width=1,
            border_color=COLOR_BORDER,
            height=60,
        )
        self._actions_frame.grid(row=2, column=0, sticky="ew", padx=0, pady=0)
        self._actions_frame.grid_propagate(False)
        self._actions_frame.grid_columnconfigure(0, weight=1)
        self._actions_frame.grid_rowconfigure(0, weight=1)

        self._actions_inner = ctk.CTkFrame(self._actions_frame, fg_color="transparent")
        self._actions_inner.pack(fill="both", expand=True, padx=16, pady=10)

        # Left action: Clear
        self._clear_btn = ctk.CTkButton(
            self._actions_inner,
            text="🗑  Clear",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            fg_color="transparent",
            border_width=1,
            border_color=COLOR_BORDER,
            text_color=COLOR_TEXT_SECONDARY,
            hover_color=("#cbd5e1", "#334155"),
            height=38,
            width=90,
            corner_radius=8,
            command=self._clear_all,
        )
        self._clear_btn.pack(side="left")

        # Right actions: Remove Background & Save
        self._save_btn = ctk.CTkButton(
            self._actions_inner,
            text="💾  Save Image",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color=COLOR_SUCCESS,
            hover_color=("#059669", "#10b981"),
            text_color=("#ffffff", "#ffffff"),
            height=38,
            corner_radius=8,
            state="disabled",
            command=self._save_image,
        )
        self._save_btn.pack(side="right", padx=(10, 0))

        self._remove_btn = ctk.CTkButton(
            self._actions_inner,
            text="✨  Remove Background",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_HOVER,
            text_color=("#ffffff", "#ffffff"),
            height=38,
            corner_radius=8,
            state="disabled",
            command=self._remove_background,
        )
        self._remove_btn.pack(side="right")

    def _select_image(self) -> None:
        """Open file dialog to choose an image file."""
        file_path_str = filedialog.askopenfilename(
            title="Select Image to Remove Background",
            filetypes=[
                ("Supported Images", "*.jpg *.jpeg *.png *.webp"),
                ("JPEG Images", "*.jpg *.jpeg"),
                ("PNG Images", "*.png"),
                ("WEBP Images", "*.webp"),
                ("All Files", "*.*"),
            ],
        )
        if not file_path_str:
            return

        target_path = Path(file_path_str)
        is_valid, error_msg = validate_image(target_path)
        if not is_valid:
            messagebox.showerror("Invalid Image", error_msg)
            return

        try:
            self._current_image_path = target_path
            self._original_pil = Image.open(target_path)
            self._result_image = None

            # Update preview
            self._preview.set_original(self._original_pil)
            self._preview._result_label.configure(
                text="✨\n\nClick 'Remove Background' below\nto process this image",
                image=None,
            )
            self._preview._result_info.configure(text="")

            # Update upload status bar and file info
            info = get_image_info(target_path)
            self._upload_label.configure(
                text=f"Selected: {info['filename']}  |  {info['size_str']}  |  {info['dimensions']} ({info['format']})",
                text_color=COLOR_TEXT,
            )

            self._remove_btn.configure(state="normal")
            self._save_btn.configure(state="disabled")
            self._status_bar.set_status(f"Loaded: {target_path.name}. Ready to process.", "info")

        except Exception as exc:
            messagebox.showerror("Error Opening Image", f"Failed to open image:\n{exc}")

    def _remove_background(self) -> None:
        """Initiate background removal using worker thread."""
        if not self._current_image_path or not self._current_image_path.exists():
            messagebox.showwarning("No Image", "Please select a valid image file first.")
            return

        # Disable interactive buttons while processing
        self._remove_btn.configure(state="disabled")
        self._select_btn.configure(state="disabled")
        self._save_btn.configure(state="disabled")
        self._clear_btn.configure(state="disabled")

        self._status_bar.set_status(
            f"Removing background with {self._processor.model_name}...", "processing"
        )
        self._preview._result_label.configure(
            text="⏳\n\nAI is removing the background...\nPlease wait a moment.",
            image=None,
        )

        task = ProcessingTask(self._current_image_path, task_id=1)
        self._worker = ProcessingWorker(
            processor=self._processor,
            on_task_update=self._on_task_update,
            on_complete=self._on_task_complete,
        )
        self._worker.process_single(task)

    def _on_task_update(self, task: ProcessingTask) -> None:
        """Marshal task update callback to the main GUI thread."""
        self.after(0, self._update_ui_for_task, task)

    def _update_ui_for_task(self, task: ProcessingTask) -> None:
        """Update UI based on intermediate task progress."""
        if task.status == TaskStatus.PROCESSING:
            self._status_bar.set_status(
                f"Processing '{task.file_path.name}' with {self._processor.model_name}...",
                "processing",
            )

    def _on_task_complete(self, task: ProcessingTask) -> None:
        """Marshal task completion callback to the main GUI thread."""
        self.after(0, self._handle_completion, task)

    def _handle_completion(self, task: ProcessingTask) -> None:
        """Handle worker completion on the main GUI thread."""
        # Restore button interactivity
        self._select_btn.configure(state="normal")
        self._clear_btn.configure(state="normal")

        if task.status == TaskStatus.COMPLETED and task.result is not None:
            self._result_image = task.result
            self._preview.set_result(self._result_image)
            self._save_btn.configure(state="normal")
            self._remove_btn.configure(state="normal")
            self._status_bar.set_status("Background removed successfully!", "success")
        elif task.status == TaskStatus.FAILED:
            self._remove_btn.configure(state="normal")
            self._save_btn.configure(state="disabled")
            self._status_bar.set_status(f"Processing failed: {task.error_message}", "error")
            self._preview._result_label.configure(
                text=f"✕\n\nProcessing failed:\n{task.error_message}",
                image=None,
            )
            # Record failed event in history
            self._history.add_entry(
                input_path=str(task.file_path),
                output_path="",
                model=self._processor.model_name,
                status=f"Failed: {task.error_message}",
            )
            messagebox.showerror("Processing Failed", f"AI background removal failed:\n{task.error_message}")
        elif task.status == TaskStatus.CANCELLED:
            self._remove_btn.configure(state="normal")
            self._status_bar.set_status("Processing was cancelled", "info")

    def _save_image(self) -> None:
        """Save the processed result image as a transparent PNG."""
        if self._result_image is None or self._current_image_path is None:
            messagebox.showwarning("Nothing to Save", "No processed image is available to save.")
            return

        # Determine default output directory and filename
        configured_out_dir = self._settings.output_directory
        if configured_out_dir and Path(configured_out_dir).is_dir():
            default_dir = configured_out_dir
        else:
            default_dir = str(self._current_image_path.parent)

        default_filename = get_output_filename(self._current_image_path)

        save_path_str = filedialog.asksaveasfilename(
            title="Save Transparent Image",
            initialdir=default_dir,
            initialfile=default_filename,
            defaultextension=".png",
            filetypes=[("PNG Transparent Image", "*.png")],
        )

        if not save_path_str:
            return

        try:
            save_path = Path(save_path_str)
            self._result_image.save(save_path, format="PNG")
            self._status_bar.set_status(f"Saved: {save_path.name}", "success")

            # Add successful record to history
            self._history.add_entry(
                input_path=str(self._current_image_path),
                output_path=str(save_path),
                model=self._processor.model_name,
                status="Completed",
            )
            messagebox.showinfo("Saved Successfully", f"Image saved successfully to:\n{save_path}")
        except Exception as exc:
            messagebox.showerror("Save Error", f"Failed to save image:\n{exc}")

    def _clear_all(self) -> None:
        """Clear current image selections and reset view."""
        self._current_image_path = None
        self._original_pil = None
        self._result_image = None
        self._preview.clear()
        self._upload_label.configure(
            text="Upload an image to remove background (Supports JPG, PNG, WEBP)",
            text_color=COLOR_TEXT_SECONDARY,
        )
        self._remove_btn.configure(state="disabled")
        self._save_btn.configure(state="disabled")
        self._status_bar.set_status("Ready", "info")
