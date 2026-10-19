"""Image utility functions for BG Remover MauL."""

from pathlib import Path
from typing import Dict, Optional, Tuple, Union
from PIL import Image, ImageDraw

SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.webp'}


def validate_image(file_path: Union[Path, str]) -> Tuple[bool, str]:
    """Validate that a file is a supported and uncorrupted image.
    
    Args:
        file_path: Path to the image file to validate.
        
    Returns:
        Tuple of (is_valid, message).
    """
    path = Path(file_path)
    if not path.exists():
        return False, f"File does not exist: {path.name}"
    
    if not path.is_file():
        return False, f"Path is not a regular file: {path.name}"
    
    if path.suffix.lower() not in SUPPORTED_FORMATS:
        supported_str = ", ".join(sorted(SUPPORTED_FORMATS))
        return False, f"Unsupported file format '{path.suffix}'. Supported formats: {supported_str}"
    
    try:
        with Image.open(path) as img:
            img.verify()
        # Verify can leave file pointer at end; re-open and load to ensure pixels can be read
        with Image.open(path) as img:
            img.load()
    except Exception as exc:
        return False, f"Corrupted or invalid image: {exc}"
    
    return True, "Valid image"


def create_thumbnail(image: Image.Image, max_size: Tuple[int, int] = (200, 200)) -> Image.Image:
    """Create a proportionally scaled thumbnail. Does NOT modify the original image.
    
    Args:
        image: Original PIL Image.
        max_size: Maximum (width, height) bounding box.
        
    Returns:
        New scaled PIL Image.
    """
    thumb = image.copy()
    resample_method = getattr(getattr(Image, 'Resampling', Image), 'LANCZOS', Image.LANCZOS)
    thumb.thumbnail(max_size, resample=resample_method)
    return thumb


def create_checkerboard(width: int, height: int, cell_size: int = 10) -> Image.Image:
    """Create a checkerboard pattern image for showing transparency.
    
    Args:
        width: Width of the checkerboard in pixels.
        height: Height of the checkerboard in pixels.
        cell_size: Size in pixels of each square check.
        
    Returns:
        RGB PIL Image filled with checkerboard pattern.
    """
    width = max(1, int(width))
    height = max(1, int(height))
    cell_size = max(1, int(cell_size))
    
    # Base image is white (#ffffff)
    checker = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(checker)
    gray_color = (204, 204, 204)  # #cccccc
    
    for y in range(0, height, cell_size):
        for x in range(0, width, cell_size):
            if ((x // cell_size) + (y // cell_size)) % 2 == 1:
                draw.rectangle(
                    [x, y, min(x + cell_size - 1, width - 1), min(y + cell_size - 1, height - 1)],
                    fill=gray_color
                )
    return checker


def overlay_on_checkerboard(image: Image.Image) -> Image.Image:
    """Overlay an RGBA image on a checkerboard to visualize transparency.
    
    Args:
        image: PIL Image (RGBA or RGB).
        
    Returns:
        RGB PIL Image with transparency composited over checkerboard.
    """
    rgba_img = image if image.mode == 'RGBA' else image.convert('RGBA')
    checker = create_checkerboard(rgba_img.width, rgba_img.height, cell_size=12)
    checker.paste(rgba_img, (0, 0), mask=rgba_img.split()[3])
    return checker


def scale_image_proportional(image: Image.Image, max_width: int, max_height: int) -> Image.Image:
    """Scale image proportionally to fit within bounds.
    
    Args:
        image: Original PIL Image.
        max_width: Maximum allowed width.
        max_height: Maximum allowed height.
        
    Returns:
        Proportionally scaled PIL Image.
    """
    if max_width <= 0 or max_height <= 0 or image.width == 0 or image.height == 0:
        return image.copy()
    
    ratio = min(max_width / image.width, max_height / image.height)
    new_width = max(1, int(round(image.width * ratio)))
    new_height = max(1, int(round(image.height * ratio)))
    
    resample_method = getattr(getattr(Image, 'Resampling', Image), 'LANCZOS', Image.LANCZOS)
    return image.resize((new_width, new_height), resample=resample_method)


def get_file_size_str(file_path: Union[Path, str]) -> str:
    """Return human-readable file size string (B, KB, or MB).
    
    Args:
        file_path: Path to the file.
        
    Returns:
        Formatted size string, e.g. '1.5 MB' or '320.0 KB'.
    """
    path = Path(file_path)
    if not path.exists():
        return "0 B"
    
    try:
        size_bytes = path.stat().st_size
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.2f} MB"
    except OSError:
        return "Unknown"


def get_image_info(file_path: Union[Path, str]) -> Dict[str, Union[str, int]]:
    """Return dict with filename, size_str, dimensions, width, height, and format.
    
    Args:
        file_path: Path to the image file.
        
    Returns:
        Dictionary containing metadata attributes.
    """
    path = Path(file_path)
    width, height = 0, 0
    fmt = path.suffix.lstrip('.').upper() if path.suffix else "Unknown"
    
    if path.exists() and path.is_file():
        try:
            with Image.open(path) as img:
                width, height = img.size
                if img.format:
                    fmt = img.format.upper()
        except Exception:
            pass
            
    return {
        "filename": path.name,
        "size_str": get_file_size_str(path),
        "dimensions": f"{width}x{height}",
        "width": width,
        "height": height,
        "format": fmt,
    }
