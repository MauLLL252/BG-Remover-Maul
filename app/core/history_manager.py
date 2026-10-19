"""Processing history manager with JSON persistence."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from app.utils.file_utils import get_app_data_dir


class HistoryManager:
    """Manages metadata history of processed images."""

    MAX_ENTRIES = 100

    def __init__(self, history_file: Optional[Path] = None):
        """Initialize history manager and load entries from disk.
        
        Args:
            history_file: Optional path override for testing. Defaults to ~/BGRemoverMauL/history.json.
        """
        self._history_file = history_file or (get_app_data_dir() / 'history.json')
        self._entries: List[Dict[str, Any]] = []
        self.load()

    def load(self) -> None:
        """Load history entries from JSON file with error resilience."""
        if self._history_file.exists():
            try:
                with open(self._history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self._entries = data[:self.MAX_ENTRIES]
                    else:
                        self._entries = []
                        self.save()
            except (json.JSONDecodeError, OSError):
                self._entries = []
                self.save()
        else:
            self._entries = []
            self.save()

    def save(self) -> None:
        """Persist history entries to JSON file."""
        try:
            self._history_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self._history_file, 'w', encoding='utf-8') as f:
                json.dump(self._entries, f, indent=4)
        except OSError:
            pass

    def add_entry(self, input_path: str, output_path: str, model: str, status: str) -> Dict[str, Any]:
        """Add a processing entry to the front of history.
        
        Stores metadata only, NOT copies of images. Caps at MAX_ENTRIES.
        
        Args:
            input_path: Source image file path.
            output_path: Destination image file path.
            model: AI model used for processing.
            status: Status string (e.g. 'Completed', 'Failed').
            
        Returns:
            The newly created history entry dictionary.
        """
        entry: Dict[str, Any] = {
            'timestamp': datetime.now().isoformat(),
            'input_file': str(input_path),
            'output_file': str(output_path),
            'model': str(model),
            'status': str(status),
        }
        self._entries.insert(0, entry)
        if len(self._entries) > self.MAX_ENTRIES:
            self._entries = self._entries[:self.MAX_ENTRIES]
        self.save()
        return entry

    def get_entries(self) -> List[Dict[str, Any]]:
        """Return a copy of all history entries, newest first."""
        return list(self._entries)

    def clear(self) -> None:
        """Clear all stored history entries and update persistence."""
        self._entries.clear()
        self.save()
