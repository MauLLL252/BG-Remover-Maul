"""File and path management utility functions for BG Remover MauL."""

from pathlib import Path
from typing import Union


def get_output_filename(input_path: Union[Path, str], suffix: str = '_no-bg') -> str:
    """Generate output filename: original-name_no-bg.png.
    
    Args:
        input_path: Path or filename of the original input image.
        suffix: Suffix to append to the file stem. Defaults to '_no-bg'.
        
    Returns:
        Formatted output filename ending in .png.
    """
    path = Path(input_path)
    return f"{path.stem}{suffix}.png"


def get_unique_filepath(directory: Union[Path, str], filename: str) -> Path:
    """If file exists in the directory, append (1), (2), etc. to avoid overwriting.
    
    Args:
        directory: Destination directory.
        filename: Target filename.
        
    Returns:
        Path that is guaranteed not to exist yet in directory.
    """
    dir_path = Path(directory)
    ensure_directory(dir_path)
    
    candidate = dir_path / filename
    if not candidate.exists():
        return candidate
    
    target_path = Path(filename)
    stem = target_path.stem
    suffix = target_path.suffix
    counter = 1
    
    while True:
        candidate = dir_path / f"{stem} ({counter}){suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def ensure_directory(directory: Union[Path, str]) -> Path:
    """Create directory if it doesn't exist and return the Path.
    
    Args:
        directory: Directory path to create.
        
    Returns:
        Path object pointing to the ensured directory.
    """
    dir_path = Path(directory)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def get_app_data_dir() -> Path:
    """Return app data directory: ~/BGRemoverMauL/
    
    Returns:
        Path object pointing to ~/BGRemoverMauL/, created if missing.
    """
    app_dir = Path.home() / 'BGRemoverMauL'
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir
