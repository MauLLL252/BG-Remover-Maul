"""Background worker thread and task tracking for image processing."""

import threading
from enum import Enum
from pathlib import Path
from typing import Callable, List, Optional
from PIL import Image


class TaskStatus(Enum):
    """Execution status for image processing tasks."""
    WAITING = 'Waiting'
    PROCESSING = 'Processing'
    COMPLETED = 'Completed'
    FAILED = 'Failed'
    CANCELLED = 'Cancelled'


class ProcessingTask:
    """Represents a single image background removal job."""

    def __init__(self, file_path: Path, task_id: int):
        """Initialize a processing task.
        
        Args:
            file_path: Path to the target image file.
            task_id: Unique identifier for this task in the queue.
        """
        self.file_path = Path(file_path)
        self.task_id = task_id
        self.status = TaskStatus.WAITING
        self.result: Optional[Image.Image] = None
        self.error_message: str = ''
        self.cancelled: bool = False

    def __repr__(self) -> str:
        return f"<ProcessingTask id={self.task_id} file={self.file_path.name} status={self.status.value}>"


class ProcessingWorker:
    """Worker that executes background removal tasks asynchronously in a background thread.
    
    IMPORTANT NOTE ON THREAD SAFETY:
    Callbacks (on_task_update and on_complete) are triggered from the worker background thread.
    When updating UI elements in Tkinter or CustomTkinter, callers MUST marshal UI updates
    to the main thread using root.after() or widget.after():
        worker = ProcessingWorker(
            processor,
            on_task_update=lambda t: root.after(0, update_ui_status, t),
            on_complete=lambda t: root.after(0, handle_completed_task, t)
        )
    """

    def __init__(
        self,
        processor,
        on_task_update: Optional[Callable[[ProcessingTask], None]] = None,
        on_complete: Optional[Callable[[ProcessingTask], None]] = None,
    ):
        """Initialize ProcessingWorker.
        
        Args:
            processor: BGRemover instance used to perform inference.
            on_task_update: Callback invoked whenever a task's status changes.
            on_complete: Callback invoked when a task finishes (COMPLETED, FAILED, or CANCELLED).
        """
        self._processor = processor
        self._on_task_update = on_task_update
        self._on_complete = on_complete
        self._thread: Optional[threading.Thread] = None
        self._cancel_event = threading.Event()
        self._is_running: bool = False

    def _notify(self, callback: Optional[Callable[[ProcessingTask], None]], task: ProcessingTask) -> None:
        """Safely invoke callback function catching any internal exceptions."""
        if callback is not None:
            try:
                callback(task)
            except Exception:
                pass

    def process_single(self, task: ProcessingTask) -> None:
        """Process a single task in a background daemon thread.
        
        Args:
            task: ProcessingTask instance to execute.
        """
        self._cancel_event.clear()
        self._thread = threading.Thread(
            target=self._run_single,
            args=(task,),
            name=f"Worker-Single-{task.task_id}",
            daemon=True,
        )
        self._thread.start()

    def process_batch(self, tasks: List[ProcessingTask]) -> None:
        """Process multiple tasks sequentially in a background daemon thread.
        
        Args:
            tasks: List of ProcessingTask instances to execute.
        """
        self._cancel_event.clear()
        self._thread = threading.Thread(
            target=self._run_batch,
            args=(tasks,),
            name="Worker-Batch",
            daemon=True,
        )
        self._thread.start()

    def cancel(self) -> None:
        """Signal cancellation. The currently executing task will complete its step,
        and all subsequent pending tasks will be cancelled.
        """
        self._cancel_event.set()

    def _run_single(self, task: ProcessingTask) -> None:
        """Internal execution loop for a single task."""
        self._is_running = True
        try:
            if self._cancel_event.is_set():
                task.status = TaskStatus.CANCELLED
                task.cancelled = True
                self._notify(self._on_task_update, task)
                self._notify(self._on_complete, task)
                return

            task.status = TaskStatus.PROCESSING
            self._notify(self._on_task_update, task)

            try:
                result = self._processor.remove_background(task.file_path)
                if self._cancel_event.is_set():
                    task.status = TaskStatus.CANCELLED
                    task.cancelled = True
                else:
                    task.result = result
                    task.status = TaskStatus.COMPLETED
            except Exception as exc:
                task.status = TaskStatus.FAILED
                task.error_message = str(exc)

            self._notify(self._on_task_update, task)
            self._notify(self._on_complete, task)
        finally:
            self._is_running = False

    def _run_batch(self, tasks: List[ProcessingTask]) -> None:
        """Internal execution loop for sequential batch processing."""
        self._is_running = True
        try:
            for task in tasks:
                if self._cancel_event.is_set():
                    task.status = TaskStatus.CANCELLED
                    task.cancelled = True
                    self._notify(self._on_task_update, task)
                    self._notify(self._on_complete, task)
                    continue

                task.status = TaskStatus.PROCESSING
                self._notify(self._on_task_update, task)

                try:
                    result = self._processor.remove_background(task.file_path)
                    if self._cancel_event.is_set():
                        task.status = TaskStatus.CANCELLED
                        task.cancelled = True
                    else:
                        task.result = result
                        task.status = TaskStatus.COMPLETED
                except Exception as exc:
                    task.status = TaskStatus.FAILED
                    task.error_message = str(exc)

                self._notify(self._on_task_update, task)
                self._notify(self._on_complete, task)
        finally:
            self._is_running = False

    @property
    def is_running(self) -> bool:
        """Return True if the worker thread is actively processing tasks."""
        return self._is_running and (self._thread is not None and self._thread.is_alive())
