"""AI Background removal processor using rembg."""

import io
from pathlib import Path
from typing import Optional, Union
from PIL import Image


class BGRemover:
    """Wrapper around rembg for AI-powered background removal."""

    def __init__(self, model_name: str = 'u2net'):
        """Initialize BGRemover with specified model.
        
        Args:
            model_name: Name of the rembg model to use (e.g. 'u2net', 'u2net_human_seg', 'isnet-general-use').
        """
        self._model_name = model_name
        self._session = None

    def _ensure_session(self) -> None:
        """Lazily create rembg session. Downloads model files on first use if not cached."""
        if self._session is None:
            try:
                from rembg import new_session
                self._session = new_session(self._model_name)
            except Exception as exc:
                raise RuntimeError(
                    f"Failed to initialize AI model session for '{self._model_name}': {exc}"
                ) from exc

    def change_model(self, model_name: str) -> None:
        """Change active AI model. Closes existing session.
        
        Args:
            model_name: New model name to switch to.
        """
        if model_name != self._model_name:
            self.close()
            self._model_name = model_name

    def remove_background(self, input_path: Union[Path, str]) -> Image.Image:
        """Remove background from image at input_path. Returns RGBA PIL Image.
        
        Args:
            input_path: Path to the image file.
            
        Returns:
            RGBA PIL Image with background removed.
            
        Raises:
            FileNotFoundError: If the input file does not exist.
            ValueError: If the file is not a valid or supported image.
            RuntimeError: If memory exhaustion or AI processing fails.
        """
        path = Path(input_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        if not path.is_file():
            raise ValueError(f"Path is not a regular file: {path}")

        # 1. Open the image from disk
        try:
            with Image.open(path) as img:
                img.load()
                # 2. Convert to bytes using io.BytesIO
                buffer = io.BytesIO()
                temp_img = img
                if temp_img.mode not in ('RGB', 'RGBA', 'L'):
                    temp_img = temp_img.convert('RGB')
                temp_img.save(buffer, format='PNG')
                image_bytes = buffer.getvalue()
        except (FileNotFoundError, ValueError):
            raise
        except Exception as exc:
            raise ValueError(f"Invalid or corrupted image '{path.name}': {exc}") from exc

        # 3. Call rembg.remove() with session parameter
        try:
            self._ensure_session()
            from rembg import remove
            output_bytes = remove(image_bytes, session=self._session)

            # 4. Return result as RGBA PIL Image
            result_img = Image.open(io.BytesIO(output_bytes))
            if result_img.mode != 'RGBA':
                result_img = result_img.convert('RGBA')
            result_img.load()
            return result_img
        except MemoryError as exc:
            raise RuntimeError(f"Out of memory while processing '{path.name}': {exc}") from exc
        except Exception as exc:
            raise RuntimeError(f"Background removal failed for '{path.name}': {exc}") from exc

    def remove_background_from_image(self, image: Image.Image) -> Image.Image:
        """Remove background directly from a PIL Image in memory.
        
        Args:
            image: PIL Image object.
            
        Returns:
            RGBA PIL Image with background removed.
            
        Raises:
            RuntimeError: If memory exhaustion or AI processing fails.
        """
        try:
            buffer = io.BytesIO()
            temp_img = image
            if temp_img.mode not in ('RGB', 'RGBA', 'L'):
                temp_img = temp_img.convert('RGB')
            temp_img.save(buffer, format='PNG')
            image_bytes = buffer.getvalue()

            self._ensure_session()
            from rembg import remove
            output_bytes = remove(image_bytes, session=self._session)

            result_img = Image.open(io.BytesIO(output_bytes))
            if result_img.mode != 'RGBA':
                result_img = result_img.convert('RGBA')
            result_img.load()
            return result_img
        except MemoryError as exc:
            raise RuntimeError(f"Out of memory while processing image: {exc}") from exc
        except Exception as exc:
            raise RuntimeError(f"Background removal failed: {exc}") from exc

    def is_model_ready(self) -> bool:
        """Check if the ONNX model files exist in local cache."""
        model_file = Path.home() / '.u2net' / f'{self._model_name}.onnx'
        return model_file.exists()

    def get_model_path(self) -> Path:
        """Return directory where rembg downloads model files (~/.u2net/)."""
        return Path.home() / '.u2net'

    def close(self) -> None:
        """Release session resources."""
        self._session = None

    @property
    def model_name(self) -> str:
        """Current AI model name."""
        return self._model_name
