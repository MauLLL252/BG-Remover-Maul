import pytest
from PIL import Image
from pathlib import Path
from app.utils.image_utils import (
    validate_image, create_thumbnail, create_checkerboard,
    overlay_on_checkerboard, scale_image_proportional,
    get_file_size_str, get_image_info, SUPPORTED_FORMATS
)

class TestValidateImage:
    def test_valid_png(self, sample_image):
        is_valid, msg = validate_image(sample_image)
        assert is_valid is True
    
    def test_valid_jpg(self, sample_image_jpg):
        is_valid, msg = validate_image(sample_image_jpg)
        assert is_valid is True
    
    def test_invalid_file(self, invalid_file):
        is_valid, msg = validate_image(invalid_file)
        assert is_valid is False
        assert len(msg) > 0  # Should have error message
    
    def test_unsupported_extension(self, unsupported_file):
        is_valid, msg = validate_image(unsupported_file)
        assert is_valid is False
    
    def test_nonexistent_file(self):
        is_valid, msg = validate_image(Path('nonexistent.png'))
        assert is_valid is False

class TestCreateThumbnail:
    def test_creates_smaller_image(self, sample_image):
        img = Image.open(sample_image)
        thumb = create_thumbnail(img, (50, 50))
        assert thumb.width <= 50
        assert thumb.height <= 50
    
    def test_does_not_modify_original(self, sample_image):
        img = Image.open(sample_image)
        original_size = img.size
        create_thumbnail(img, (50, 50))
        assert img.size == original_size  # Original unchanged

class TestCreateCheckerboard:
    def test_correct_size(self):
        cb = create_checkerboard(100, 80)
        assert cb.size == (100, 80)
    
    def test_is_rgb(self):
        cb = create_checkerboard(50, 50)
        assert cb.mode == 'RGB'

class TestOverlayOnCheckerboard:
    def test_output_is_rgb(self, sample_rgba_image):
        img = Image.open(sample_rgba_image)
        result = overlay_on_checkerboard(img)
        assert result.mode == 'RGB'
    
    def test_same_size(self, sample_rgba_image):
        img = Image.open(sample_rgba_image)
        result = overlay_on_checkerboard(img)
        assert result.size == img.size

class TestScaleImageProportional:
    def test_scales_down(self):
        img = Image.new('RGB', (1000, 500))
        scaled = scale_image_proportional(img, 200, 200)
        assert scaled.width <= 200
        assert scaled.height <= 200
    
    def test_maintains_aspect_ratio(self):
        img = Image.new('RGB', (1000, 500))  # 2:1 ratio
        scaled = scale_image_proportional(img, 200, 200)
        ratio = scaled.width / scaled.height
        assert abs(ratio - 2.0) < 0.1  # Should maintain ~2:1

class TestGetFileSizeStr:
    def test_returns_string(self, sample_image):
        size_str = get_file_size_str(sample_image)
        assert isinstance(size_str, str)
        assert len(size_str) > 0

class TestGetImageInfo:
    def test_returns_dict(self, sample_image):
        info = get_image_info(sample_image)
        assert 'filename' in info
        assert 'size_str' in info
        assert 'dimensions' in info
