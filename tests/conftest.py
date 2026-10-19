import pytest
from PIL import Image, ImageDraw
from pathlib import Path
import tempfile
import shutil

@pytest.fixture
def temp_dir():
    """Create and cleanup a temporary directory."""
    d = Path(tempfile.mkdtemp())
    yield d
    shutil.rmtree(d, ignore_errors=True)

@pytest.fixture
def sample_image(temp_dir) -> Path:
    """Create a 200x200 test image: bright red circle on white background.
    This provides contrast for background removal testing."""
    img = Image.new('RGB', (200, 200), (255, 255, 255))  # white bg
    draw = ImageDraw.Draw(img)
    draw.ellipse([50, 50, 150, 150], fill=(255, 0, 0))  # red circle
    path = temp_dir / 'test_image.png'
    img.save(path)
    return path

@pytest.fixture
def sample_image_jpg(temp_dir) -> Path:
    """Create a JPG test image."""
    img = Image.new('RGB', (200, 200), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.ellipse([50, 50, 150, 150], fill=(0, 0, 255))  # blue circle
    path = temp_dir / 'test_image.jpg'
    img.save(path, 'JPEG')
    return path

@pytest.fixture
def sample_rgba_image(temp_dir) -> Path:
    """Create an RGBA image with transparency."""
    img = Image.new('RGBA', (200, 200), (0, 0, 0, 0))  # fully transparent
    draw = ImageDraw.Draw(img)
    draw.ellipse([50, 50, 150, 150], fill=(255, 0, 0, 255))  # opaque red circle
    path = temp_dir / 'test_rgba.png'
    img.save(path)
    return path

@pytest.fixture
def invalid_file(temp_dir) -> Path:
    """Create a non-image file with .png extension."""
    path = temp_dir / 'not_an_image.png'
    path.write_text('this is not an image')
    return path

@pytest.fixture
def unsupported_file(temp_dir) -> Path:
    """Create a file with unsupported extension."""
    path = temp_dir / 'document.pdf'
    path.write_text('fake pdf content')
    return path
