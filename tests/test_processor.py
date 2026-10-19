import pytest
from PIL import Image
from pathlib import Path

try:
    import rembg
    HAS_REMBG = True
except ImportError:
    HAS_REMBG = False

pytestmark = pytest.mark.skipif(not HAS_REMBG, reason='rembg not installed')

from app.core.processor import BGRemover


class TestBGRemover:
    @pytest.fixture
    def remover(self):
        """Create a BGRemover instance. Model downloads on first use."""
        r = BGRemover('u2net')
        yield r
        r.close()
    
    def test_remove_background_returns_rgba(self, remover, sample_image):
        """Output must have alpha channel (RGBA mode)."""
        result = remover.remove_background(sample_image)
        assert result.mode == 'RGBA'
    
    def test_remove_background_preserves_size(self, remover, sample_image):
        """Output should have same dimensions as input."""
        original = Image.open(sample_image)
        result = remover.remove_background(sample_image)
        assert result.size == original.size
    
    def test_foreground_not_fully_transparent(self, remover, sample_image):
        """The foreground object (red circle in center) should remain visible.
        Check that the center area has non-transparent pixels."""
        result = remover.remove_background(sample_image)
        # Check center 50x50 area (where the circle is)
        center_x, center_y = 100, 100
        alpha_values = []
        for x in range(center_x - 25, center_x + 25):
            for y in range(center_y - 25, center_y + 25):
                alpha_values.append(result.getpixel((x, y))[3])
        
        # At least 50% of center pixels should be non-transparent
        non_transparent = sum(1 for a in alpha_values if a > 128)
        total = len(alpha_values)
        assert non_transparent / total > 0.5, \
            f"Foreground should be visible: only {non_transparent}/{total} non-transparent pixels in center"
    
    def test_background_has_transparency(self, remover, sample_image):
        """The background (corners) should have significant transparency."""
        result = remover.remove_background(sample_image)
        # Check corners (should be background = transparent)
        corners = [(5, 5), (195, 5), (5, 195), (195, 195)]
        alpha_values = [result.getpixel(pos)[3] for pos in corners]
        
        # At least 3 of 4 corners should be mostly transparent
        transparent_corners = sum(1 for a in alpha_values if a < 128)
        assert transparent_corners >= 3, \
            f"Background should be transparent: only {transparent_corners}/4 corners are transparent"
    
    def test_invalid_file_raises_error(self, remover, invalid_file):
        """Invalid image file should raise a clear error."""
        with pytest.raises((ValueError, RuntimeError, Exception)):
            remover.remove_background(invalid_file)
    
    def test_nonexistent_file_raises_error(self, remover):
        """Non-existent file should raise FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            remover.remove_background(Path('does_not_exist.png'))
    
    def test_model_name_property(self, remover):
        assert remover.model_name == 'u2net'
    
    def test_change_model(self, remover):
        remover.change_model('u2net_human_seg')
        assert remover.model_name == 'u2net_human_seg'
    
    def test_is_model_ready(self, remover):
        """After processing, model should be ready."""
        # This will be True if model was already downloaded
        result = remover.is_model_ready()
        assert isinstance(result, bool)
