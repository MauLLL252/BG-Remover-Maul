"""Settings management for BG Remover MauL."""

import json
from pathlib import Path
from typing import Any, Dict
from app.utils.file_utils import get_app_data_dir

DEFAULT_SETTINGS = {
    'theme': 'dark',
    'output_directory': '',
    'ai_model': 'u2net',
    'window_width': 1200,
    'window_height': 750,
}

AVAILABLE_MODELS = {
    'u2net': {
        'name': 'U2-Net (General)',
        'description': 'Model umum untuk berbagai jenis gambar',
        'license': 'Apache 2.0',
    },
    'u2net_human_seg': {
        'name': 'U2-Net Human',
        'description': 'Dioptimalkan untuk segmentasi manusia',
        'license': 'Apache 2.0',
    },
    'isnet-general-use': {
        'name': 'ISNet General',
        'description': 'Model alternatif dengan akurasi tinggi',
        'license': 'Apache 2.0',
    },
}

COLOR_PALETTES = {
    'dark': {
        'bg': '#0f172a',
        'sidebar': '#1e293b',
        'card': '#1e3a5f',
        'accent': '#3b82f6',
        'hover': '#60a5fa',
        'success': '#10b981',
        'error': '#ef4444',
        'text': '#f1f5f9',
        'text2': '#94a3b8',
        'border': '#334155',
    },
    'light': {
        'bg': '#f1f5f9',
        'sidebar': '#e2e8f0',
        'card': '#ffffff',
        'accent': '#2563eb',
        'hover': '#1d4ed8',
        'success': '#10b981',
        'error': '#ef4444',
        'text': '#0f172a',
        'text2': '#64748b',
        'border': '#cbd5e1',
    },
}


class SettingsManager:
    """Manages application configurations with persistence to disk."""

    def __init__(self, settings_file: Path | None = None):
        """Initialize settings manager and load stored settings.
        
        Args:
            settings_file: Optional path override for testing. Defaults to ~/BGRemoverMauL/settings.json.
        """
        self._settings_file = settings_file or (get_app_data_dir() / 'settings.json')
        self._settings: Dict[str, Any] = {}
        self.load()

    def load(self) -> None:
        """Load settings from JSON file. Merges with default values for missing keys."""
        self._settings = DEFAULT_SETTINGS.copy()
        if self._settings_file.exists():
            try:
                with open(self._settings_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        self._settings.update(data)
            except (json.JSONDecodeError, OSError):
                # If corrupted or unreadable, preserve defaults and rewrite clean config
                self.save()
        else:
            self.save()

    def save(self) -> None:
        """Save settings dictionary to JSON file with indentation."""
        try:
            self._settings_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self._settings_file, 'w', encoding='utf-8') as f:
                json.dump(self._settings, f, indent=4)
        except OSError:
            pass

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve setting value by key."""
        return self._settings.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Update setting value and persist to disk."""
        self._settings[key] = value
        self.save()

    def reset(self) -> None:
        """Reset all settings back to default values."""
        self._settings = DEFAULT_SETTINGS.copy()
        self.save()

    @property
    def theme(self) -> str:
        """Current theme mode ('dark' or 'light')."""
        return str(self.get('theme', DEFAULT_SETTINGS['theme']))

    @theme.setter
    def theme(self, value: str) -> None:
        self.set('theme', value)

    @property
    def output_directory(self) -> str:
        """Default directory where output images are saved."""
        return str(self.get('output_directory', DEFAULT_SETTINGS['output_directory']))

    @output_directory.setter
    def output_directory(self, value: str) -> None:
        self.set('output_directory', value)

    @property
    def ai_model(self) -> str:
        """Active AI model key (e.g., 'u2net')."""
        return str(self.get('ai_model', DEFAULT_SETTINGS['ai_model']))

    @ai_model.setter
    def ai_model(self, value: str) -> None:
        self.set('ai_model', value)

    @property
    def window_width(self) -> int:
        """Configured main window width."""
        return int(self.get('window_width', DEFAULT_SETTINGS['window_width']))

    @property
    def window_height(self) -> int:
        """Configured main window height."""
        return int(self.get('window_height', DEFAULT_SETTINGS['window_height']))

    def get_theme_colors(self) -> Dict[str, str]:
        """Return the palette dictionary matching the current theme."""
        return COLOR_PALETTES.get(self.theme, COLOR_PALETTES['dark'])
