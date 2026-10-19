"""Side-by-side before/after image preview with checkerboard transparency."""

from typing import Optional
import customtkinter as ctk
from PIL import Image

from app.theme import (
    COLOR_CARD,
    COLOR_TEXT,
    COLOR_TEXT_SECONDARY,
    COLOR_BORDER,
    COLOR_ACCENT,
)
from app.utils.image_utils import overlay_on_checkerboard, scale_image_proportional


class ImagePreview(ctk.CTkFrame):
    """Side-by-side before/after image preview panel with checkerboard transparency."""

    MAX_PREVIEW_WIDTH = 500
    MAX_PREVIEW_HEIGHT = 400

    def __init__(self, parent, **kwargs):
        """Initialize the ImagePreview widget.
        
        Args:
            parent: Parent container widget.
            **kwargs: Extra arguments passed to CTkFrame.
        """
        super().__init__(parent, fg_color="transparent", **kwargs)

        self._original_image: Optional[Image.Image] = None
        self._result_image: Optional[Image.Image] = None
        self._tk_original: Optional[ctk.CTkImage] = None
        self._tk_result: Optional[ctk.CTkImage] = None

        # Setup side-by-side grid
        self.grid_columnconfigure(0, weight=1, uniform="preview_panel")
        self.grid_columnconfigure(1, weight=1, uniform="preview_panel")
        self.grid_rowconfigure(0, weight=1)

        # Left Panel: Original Image
        self._left_panel = ctk.CTkFrame(
            self,
            fg_color=COLOR_CARD,
            corner_radius=10,
            border_width=1,
            border_color=COLOR_BORDER,
        )
        self._left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 6), pady=0)
        self._left_panel.grid_rowconfigure(1, weight=1)
        self._left_panel.grid_columnconfigure(0, weight=1)

        self._left_header = ctk.CTkLabel(
            self._left_panel,
            text="Original Image",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=COLOR_TEXT,
        )
        self._left_header.grid(row=0, column=0, sticky="w", padx=14, pady=(10, 5))

        self._original_label = ctk.CTkLabel(
            self._left_panel,
            text="📁\n\nNo image loaded\nSelect an image to preview",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLOR_TEXT_SECONDARY,
            anchor="center",
        )
        self._original_label.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        self._original_info = ctk.CTkLabel(
            self._left_panel,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=COLOR_TEXT_SECONDARY,
        )
        self._original_info.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 8))

        # Right Panel: Result Image
        self._right_panel = ctk.CTkFrame(
            self,
            fg_color=COLOR_CARD,
            corner_radius=10,
            border_width=1,
            border_color=COLOR_BORDER,
        )
        self._right_panel.grid(row=0, column=1, sticky="nsew", padx=(6, 0), pady=0)
        self._right_panel.grid_rowconfigure(1, weight=1)
        self._right_panel.grid_columnconfigure(0, weight=1)

        self._right_header = ctk.CTkLabel(
            self._right_panel,
            text="Result (Transparent Background)",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=COLOR_TEXT,
        )
        self._right_header.grid(row=0, column=0, sticky="w", padx=14, pady=(10, 5))

        self._result_label = ctk.CTkLabel(
            self._right_panel,
            text="✨\n\nResult will appear here\nafter background removal",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLOR_TEXT_SECONDARY,
            anchor="center",
        )
        self._result_label.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        self._result_info = ctk.CTkLabel(
            self._right_panel,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=COLOR_TEXT_SECONDARY,
        )
        self._result_info.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 8))

    def set_original(self, image: Image.Image) -> None:
        """Display the original image scaled proportionally to fit the panel.
        
        Args:
            image: Original PIL Image.
        """
        self._original_image = image
        scaled = scale_image_proportional(
            image, self.MAX_PREVIEW_WIDTH, self.MAX_PREVIEW_HEIGHT
        )
        self._tk_original = ctk.CTkImage(
            light_image=scaled,
            dark_image=scaled,
            size=(scaled.width, scaled.height),
        )
        self._original_label.configure(text="", image=self._tk_original)
        self._original_info.configure(
            text=f"Resolution: {image.width} × {image.height} px | Format: {getattr(image, 'format', 'Image') or 'Image'}"
        )

    def set_result(self, image: Image.Image) -> None:
        """Display the result image overlaid on a checkerboard to show transparency.
        
        Args:
            image: RGBA PIL Image with removed background.
        """
        self._result_image = image
        checker_overlay = overlay_on_checkerboard(image)
        scaled = scale_image_proportional(
            checker_overlay, self.MAX_PREVIEW_WIDTH, self.MAX_PREVIEW_HEIGHT
        )
        self._tk_result = ctk.CTkImage(
            light_image=scaled,
            dark_image=scaled,
            size=(scaled.width, scaled.height),
        )
        self._result_label.configure(text="", image=self._tk_result)
        self._result_info.configure(
            text=f"Result: {image.width} × {image.height} px | Alpha Channel Active"
        )

    def clear(self) -> None:
        """Clear both panels and restore placeholder messages."""
        self._original_image = None
        self._result_image = None
        self._tk_original = None
        self._tk_result = None

        self._original_label.configure(
            text="📁\n\nNo image loaded\nSelect an image to preview",
            image=None,
        )
        self._original_info.configure(text="")

        self._result_label.configure(
            text="✨\n\nResult will appear here\nafter background removal",
            image=None,
        )
        self._result_info.configure(text="")

    def _update_display(self) -> None:
        """Recalculate sizes and redraw active images."""
        if self._original_image is not None:
            self.set_original(self._original_image)
        if self._result_image is not None:
            self.set_result(self._result_image)
