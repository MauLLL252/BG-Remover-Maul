"""Batch background removal processing page with queue management."""

from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Dict, List, Optional
import customtkinter as ctk
from PIL import Image

from app.components.queue_item import QueueItem
from app.core.worker import ProcessingWorker, ProcessingTask, TaskStatus
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
from app.utils.image_utils import validate_image
from app.utils.file_utils import get_output_filename, get_unique_filepath, ensure_directory


class BatchPage(ctk.CTkFrame):
    """Page for batch processing multiple images in an asynchronous queue."""

    def __init__(self, parent, processor, settings, history_manager, status_bar, **kwargs):
        """Initialize BatchPage.
        
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

        self._tasks: Dict[int, ProcessingTask] = {}
        self._queue_widgets: Dict[int, QueueItem] = {}
        self._results: Dict[int, Image.Image] = {}
        self._worker: Optional[ProcessingWorker] = None
        self._next_task_id = 1

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Build top control panel, scrollable queue, and action buttons."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)  # Queue frame expands

        # 1. Top Bar: Add Images & Summary Badge
        self._top_frame = ctk.CTkFrame(
            self,
            fg_color=COLOR_CARD,
            corner_radius=10,
            border_width=1,
            border_color=COLOR_BORDER,
            height=54,
        )
        self._top_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 10))
        self._top_frame.grid_propagate(False)
        self._top_frame.grid_columnconfigure(1, weight=1)
        self._top_frame.grid_rowconfigure(0, weight=1)

        self._add_btn = ctk.CTkButton(
            self._top_frame,
            text="➕   Add Images",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_HOVER,
            text_color=("#ffffff", "#ffffff"),
            height=36,
            corner_radius=8,
            command=self._add_images,
        )
        self._add_btn.grid(row=0, column=0, sticky="w", padx=14, pady=8)

        self._summary_label = ctk.CTkLabel(
            self._top_frame,
            text="Queue is empty",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLOR_TEXT_SECONDARY,
            anchor="e",
        )
        self._summary_label.grid(row=0, column=1, sticky="e", padx=16, pady=8)

        # 2. Middle: Scrollable Queue List
        self._scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=COLOR_CARD,
            corner_radius=10,
            border_width=1,
            border_color=COLOR_BORDER,
        )
        self._scroll_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=(0, 10))
        self._scroll_frame.grid_columnconfigure(0, weight=1)

        self._empty_label = ctk.CTkLabel(
            self._scroll_frame,
            text="📦\n\nNo images in queue\nClick 'Add Images' above to get started with batch processing",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLOR_TEXT_SECONDARY,
            justify="center",
        )
        self._empty_label.pack(pady=80)

        # 3. Bottom: Action Controls Bar
        self._bottom_frame = ctk.CTkFrame(
            self,
            fg_color=COLOR_CARD,
            corner_radius=10,
            border_width=1,
            border_color=COLOR_BORDER,
            height=60,
        )
        self._bottom_frame.grid(row=2, column=0, sticky="ew", padx=0, pady=0)
        self._bottom_frame.grid_propagate(False)
        self._bottom_frame.grid_columnconfigure(0, weight=1)
        self._bottom_frame.grid_rowconfigure(0, weight=1)

        self._bottom_inner = ctk.CTkFrame(self._bottom_frame, fg_color="transparent")
        self._bottom_inner.pack(fill="both", expand=True, padx=16, pady=10)

        # Left side: Clear Queue
        self._clear_btn = ctk.CTkButton(
            self._bottom_inner,
            text="🗑  Clear Queue",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            fg_color="transparent",
            border_width=1,
            border_color=COLOR_BORDER,
            text_color=COLOR_TEXT_SECONDARY,
            hover_color=("#cbd5e1", "#334155"),
            height=38,
            corner_radius=8,
            command=self._clear_queue,
        )
        self._clear_btn.pack(side="left")

        # Right side: Cancel, Save All, Process All
        self._cancel_btn = ctk.CTkButton(
            self._bottom_inner,
            text="⛔  Cancel",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color=COLOR_ERROR,
            hover_color=("#dc2626", "#b91c1c"),
            text_color=("#ffffff", "#ffffff"),
            height=38,
            corner_radius=8,
            state="disabled",
            command=self._cancel_processing,
        )
        self._cancel_btn.pack(side="right", padx=(10, 0))

        self._save_all_btn = ctk.CTkButton(
            self._bottom_inner,
            text="💾  Save All",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color=COLOR_SUCCESS,
            hover_color=("#059669", "#10b981"),
            text_color=("#ffffff", "#ffffff"),
            height=38,
            corner_radius=8,
            state="disabled",
            command=self._save_all,
        )
        self._save_all_btn.pack(side="right", padx=(10, 0))

        self._process_all_btn = ctk.CTkButton(
            self._bottom_inner,
            text="▶   Process All",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_HOVER,
            text_color=("#ffffff", "#ffffff"),
            height=38,
            corner_radius=8,
            state="disabled",
            command=self._process_all,
        )
        self._process_all_btn.pack(side="right")

    def _add_images(self) -> None:
        """Open multi-file picker and enqueue valid images."""
        file_paths = filedialog.askopenfilenames(
            title="Select Images for Batch Processing",
            filetypes=[
                ("Supported Images", "*.jpg *.jpeg *.png *.webp"),
                ("JPEG Images", "*.jpg *.jpeg"),
                ("PNG Images", "*.png"),
                ("WEBP Images", "*.webp"),
                ("All Files", "*.*"),
            ],
        )
        if not file_paths:
            return

        added_count = 0
        skipped_count = 0

        for path_str in file_paths:
            file_path = Path(path_str)
            is_valid, _ = validate_image(file_path)
            if not is_valid:
                skipped_count += 1
                continue

            task_id = self._next_task_id
            self._next_task_id += 1

            task = ProcessingTask(file_path=file_path, task_id=task_id)
            self._tasks[task_id] = task

            # Create queue widget
            item_widget = QueueItem(
                self._scroll_frame,
                file_path=file_path,
                task_id=task_id,
                on_remove=self._remove_from_queue,
            )
            item_widget.pack(fill="x", padx=6, pady=4)
            self._queue_widgets[task_id] = item_widget
            added_count += 1

        if added_count > 0:
            self._empty_label.pack_forget()

        self._update_summary()

        if skipped_count > 0:
            messagebox.showwarning(
                "Skipped Invalid Files",
                f"{skipped_count} file(s) were skipped because they are corrupted or not supported image formats.",
            )

    def _process_all(self) -> None:
        """Start asynchronous batch processing of all waiting tasks."""
        pending_tasks = [
            t for t in self._tasks.values()
            if t.status in (TaskStatus.WAITING, TaskStatus.FAILED, TaskStatus.CANCELLED)
        ]
        if not pending_tasks:
            messagebox.showinfo("Batch Processing", "No pending tasks to process.")
            return

        # Reset failed/cancelled tasks to WAITING for rerun
        for task in pending_tasks:
            task.status = TaskStatus.WAITING
            task.error_message = ""
            widget = self._queue_widgets.get(task.task_id)
            if widget:
                widget.update_status(TaskStatus.WAITING)

        # Toggle UI states
        self._process_all_btn.configure(state="disabled")
        self._add_btn.configure(state="disabled")
        self._clear_btn.configure(state="disabled")
        self._cancel_btn.configure(state="normal")
        self._save_all_btn.configure(state="disabled")

        self._status_bar.set_processing(1, len(pending_tasks))

        self._worker = ProcessingWorker(
            processor=self._processor,
            on_task_update=self._on_task_update,
            on_complete=self._on_task_complete,
        )
        self._worker.process_batch(pending_tasks)

    def _on_task_update(self, task: ProcessingTask) -> None:
        """Marshal task update from worker thread to GUI thread."""
        self.after(0, self._update_queue_item, task)

    def _update_queue_item(self, task: ProcessingTask) -> None:
        """Update single queue item widget during processing."""
        widget = self._queue_widgets.get(task.task_id)
        if widget:
            widget.update_status(task.status, task.error_message)

        if task.status == TaskStatus.PROCESSING:
            # Find current index
            completed_count = sum(1 for t in self._tasks.values() if t.status in (TaskStatus.COMPLETED, TaskStatus.FAILED))
            self._status_bar.set_processing(completed_count + 1, len(self._tasks))

        self._update_summary()

    def _on_task_complete(self, task: ProcessingTask) -> None:
        """Marshal task completion from worker thread to GUI thread."""
        self.after(0, self._handle_task_complete, task)

    def _handle_task_complete(self, task: ProcessingTask) -> None:
        """Handle individual task completion and inspect overall queue completion."""
        if task.status == TaskStatus.COMPLETED and task.result is not None:
            self._results[task.task_id] = task.result

        widget = self._queue_widgets.get(task.task_id)
        if widget:
            widget.update_status(task.status, task.error_message)

        self._update_summary()

        # Check if worker is done or all tasks are finished
        is_worker_active = self._worker is not None and self._worker.is_running
        any_processing_or_waiting = any(
            t.status in (TaskStatus.WAITING, TaskStatus.PROCESSING) for t in self._tasks.values()
        )

        if not is_worker_active or not any_processing_or_waiting:
            self._process_all_btn.configure(state="normal")
            self._add_btn.configure(state="normal")
            self._clear_btn.configure(state="normal")
            self._cancel_btn.configure(state="disabled")

            completed_count = sum(1 for t in self._tasks.values() if t.status == TaskStatus.COMPLETED)
            failed_count = sum(1 for t in self._tasks.values() if t.status == TaskStatus.FAILED)

            if completed_count > 0:
                self._save_all_btn.configure(state="normal")

            if completed_count + failed_count > 0:
                self._status_bar.set_status(
                    f"Batch complete: {completed_count} successful, {failed_count} failed",
                    "success" if failed_count == 0 else "info",
                )

    def _save_all(self) -> None:
        """Save all completed results as PNG files into a chosen folder."""
        completed_tasks = [
            t for t in self._tasks.values()
            if t.status == TaskStatus.COMPLETED and t.task_id in self._results
        ]
        if not completed_tasks:
            messagebox.showwarning("Save All", "There are no completed images to save.")
            return

        default_dir = self._settings.output_directory or str(Path.home())
        target_dir_str = filedialog.askdirectory(
            title="Select Folder to Save Transparent Images",
            initialdir=default_dir,
        )
        if not target_dir_str:
            return

        target_dir = Path(target_dir_str)
        ensure_directory(target_dir)

        saved_count = 0
        error_count = 0

        for task in completed_tasks:
            try:
                out_filename = get_output_filename(task.file_path)
                final_path = get_unique_filepath(target_dir, out_filename)
                img = self._results[task.task_id]
                img.save(final_path, format="PNG")
                saved_count += 1

                self._history.add_entry(
                    input_path=str(task.file_path),
                    output_path=str(final_path),
                    model=self._processor.model_name,
                    status="Completed",
                )
            except Exception:
                error_count += 1

        self._status_bar.set_status(f"Saved {saved_count} images to {target_dir.name}", "success")
        msg = f"Successfully saved {saved_count} images to:\n{target_dir}"
        if error_count > 0:
            msg += f"\n\n({error_count} images failed to save)"
        messagebox.showinfo("Batch Save Complete", msg)

    def _remove_from_queue(self, task_id: int) -> None:
        """Remove a task and its row widget from the queue."""
        task = self._tasks.get(task_id)
        if task and task.status == TaskStatus.PROCESSING:
            messagebox.showwarning("Busy", "Cannot remove an item that is actively processing.")
            return

        widget = self._queue_widgets.pop(task_id, None)
        if widget:
            widget.destroy()

        self._tasks.pop(task_id, None)
        self._results.pop(task_id, None)

        if not self._tasks:
            self._empty_label.pack(pady=80)

        self._update_summary()

    def _cancel_processing(self) -> None:
        """Cancel active batch execution."""
        if self._worker and self._worker.is_running:
            self._worker.cancel()
            self._cancel_btn.configure(state="disabled")
            self._status_bar.set_status("Cancelling batch processing...", "error")

    def _clear_queue(self) -> None:
        """Clear all tasks and widgets from the queue."""
        if self._worker and self._worker.is_running:
            if not messagebox.askyesno(
                "Cancel and Clear?",
                "Batch processing is currently in progress. Cancel operations and clear queue?",
            ):
                return
            self._worker.cancel()

        for widget in self._queue_widgets.values():
            widget.destroy()

        self._tasks.clear()
        self._queue_widgets.clear()
        self._results.clear()

        self._empty_label.pack(pady=80)
        self._update_summary()
        self._status_bar.set_status("Batch queue cleared", "info")

    def _update_summary(self) -> None:
        """Recalculate task statuses and update summary text and button states."""
        total = len(self._tasks)
        if total == 0:
            self._summary_label.configure(text="Queue is empty")
            self._process_all_btn.configure(state="disabled")
            self._save_all_btn.configure(state="disabled")
            return

        waiting = sum(1 for t in self._tasks.values() if t.status == TaskStatus.WAITING)
        processing = sum(1 for t in self._tasks.values() if t.status == TaskStatus.PROCESSING)
        completed = sum(1 for t in self._tasks.values() if t.status == TaskStatus.COMPLETED)
        failed = sum(1 for t in self._tasks.values() if t.status == TaskStatus.FAILED)
        cancelled = sum(1 for t in self._tasks.values() if t.status == TaskStatus.CANCELLED)

        summary_parts = [f"Total: {total}"]
        if waiting > 0:
            summary_parts.append(f"Waiting: {waiting}")
        if processing > 0:
            summary_parts.append(f"Processing: {processing}")
        if completed > 0:
            summary_parts.append(f"Completed: {completed}")
        if failed > 0:
            summary_parts.append(f"Failed: {failed}")
        if cancelled > 0:
            summary_parts.append(f"Cancelled: {cancelled}")

        self._summary_label.configure(text="  |  ".join(summary_parts))

        is_running = self._worker is not None and self._worker.is_running
        if not is_running:
            can_process = (waiting > 0 or failed > 0 or cancelled > 0)
            self._process_all_btn.configure(state="normal" if can_process else "disabled")
            self._save_all_btn.configure(state="normal" if completed > 0 else "disabled")
            self._cancel_btn.configure(state="disabled")
