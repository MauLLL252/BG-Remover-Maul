import pytest
from pathlib import Path
from app.utils.file_utils import (
    get_output_filename, get_unique_filepath, ensure_directory, get_app_data_dir
)

class TestGetOutputFilename:
    def test_default_suffix(self):
        result = get_output_filename(Path('photo.jpg'))
        assert result == 'photo_no-bg.png'
    
    def test_custom_suffix(self):
        result = get_output_filename(Path('image.png'), '_processed')
        assert result == 'image_processed.png'
    
    def test_preserves_stem(self):
        result = get_output_filename(Path('/some/path/my photo.jpeg'))
        assert result == 'my photo_no-bg.png'

class TestGetUniqueFilepath:
    def test_returns_original_if_not_exists(self, temp_dir):
        result = get_unique_filepath(temp_dir, 'output.png')
        assert result == temp_dir / 'output.png'
    
    def test_appends_number_if_exists(self, temp_dir):
        (temp_dir / 'output.png').touch()
        result = get_unique_filepath(temp_dir, 'output.png')
        assert result == temp_dir / 'output (1).png'
    
    def test_increments_number(self, temp_dir):
        (temp_dir / 'output.png').touch()
        (temp_dir / 'output (1).png').touch()
        result = get_unique_filepath(temp_dir, 'output.png')
        assert result == temp_dir / 'output (2).png'

class TestEnsureDirectory:
    def test_creates_directory(self, temp_dir):
        new_dir = temp_dir / 'sub' / 'dir'
        result = ensure_directory(new_dir)
        assert new_dir.exists()
        assert result == new_dir
    
    def test_existing_directory_ok(self, temp_dir):
        result = ensure_directory(temp_dir)
        assert result == temp_dir

class TestGetAppDataDir:
    def test_returns_path(self):
        result = get_app_data_dir()
        assert isinstance(result, Path)
        assert result.name == 'BGRemoverMauL'
