"""About page displaying application information, open-source credits, and disclosures."""

import customtkinter as ctk

from app.theme import (
    COLOR_CARD,
    COLOR_BORDER,
    COLOR_TEXT,
    COLOR_TEXT_SECONDARY,
    COLOR_ACCENT,
)


class AboutPage(ctk.CTkFrame):
    """Informational page with app version, technology credits, and privacy guarantees."""

    def __init__(self, parent, **kwargs):
        """Initialize AboutPage.
        
        Args:
            parent: Parent container widget.
            **kwargs: Extra arguments passed to CTkFrame.
        """
        super().__init__(parent, fg_color="transparent", **kwargs)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Construct the about page layout."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self._scroll.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self._scroll.grid_columnconfigure(0, weight=1)

        # 1. Branding Header Card
        self._header_card = ctk.CTkFrame(
            self._scroll,
            fg_color=COLOR_CARD,
            corner_radius=10,
            border_width=1,
            border_color=COLOR_BORDER,
        )
        self._header_card.pack(fill="x", padx=4, pady=(5, 12))

        header_top = ctk.CTkFrame(self._header_card, fg_color="transparent")
        header_top.pack(fill="x", padx=20, pady=(20, 6))

        app_title = ctk.CTkLabel(
            header_top,
            text="✨  BG Remover MauL",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color=COLOR_TEXT,
        )
        app_title.pack(side="left")

        version_badge = ctk.CTkLabel(
            header_top,
            text="v1.0.0",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color=COLOR_ACCENT,
            text_color=("#ffffff", "#ffffff"),
            corner_radius=6,
            padx=8,
            pady=3,
        )
        version_badge.pack(side="left", padx=(12, 0))

        subtitle = ctk.CTkLabel(
            self._header_card,
            text="Aplikasi Desktop Windows AI Penghapus Latar Belakang Foto Otomatis",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=COLOR_ACCENT,
            anchor="w",
        )
        subtitle.pack(fill="x", padx=20, pady=(0, 8))

        desc_text = (
            "BG Remover MauL adalah aplikasi desktop modern yang memungkinkan Anda menghapus background foto "
            "secara otomatis, cepat, dan presisi menggunakan model kecerdasan buatan (AI) canggih. "
            "Aplikasi ini dirancang khusus dengan tema Denim Blue yang elegan, kemudahan pemrosesan tunggal "
            "maupun antrean batch (banyak file sekaligus), serta privasi penuh bagi pengguna."
        )
        desc_label = ctk.CTkLabel(
            self._header_card,
            text=desc_text,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLOR_TEXT_SECONDARY,
            anchor="w",
            justify="left",
            wraplength=700,
        )
        desc_label.pack(fill="x", padx=20, pady=(0, 20))

        # 2. Open Source Credits Card
        self._credits_card = ctk.CTkFrame(
            self._scroll,
            fg_color=COLOR_CARD,
            corner_radius=10,
            border_width=1,
            border_color=COLOR_BORDER,
        )
        self._credits_card.pack(fill="x", padx=4, pady=(0, 12))

        credits_title = ctk.CTkLabel(
            self._credits_card,
            text="📦   Teknologi & Open Source Credits",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color=COLOR_TEXT,
            anchor="w",
        )
        credits_title.pack(fill="x", padx=20, pady=(16, 10))

        credits = [
            ("rembg", "MIT License", "Pustaka inti Python untuk segmentasi dan penghapusan background berbasis AI."),
            ("U2-Net Model", "Apache 2.0", "Model Deep Learning arsitektur Salient Object Detection (SOD) berkualitas tinggi."),
            ("CustomTkinter", "MIT License", "Modern and customizable UI library untuk Python Tkinter."),
            ("Pillow (PIL)", "HPND License", "Pustaka manipulasi, transformasi, dan pemrosesan gambar Python."),
            ("ONNX Runtime", "MIT License", "Mesin akselerasi inferensi model machine learning performa tinggi."),
        ]

        for name, license_str, desc in credits:
            row = ctk.CTkFrame(self._credits_card, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=5)

            left_stack = ctk.CTkFrame(row, fg_color="transparent")
            left_stack.pack(side="left", fill="x", expand=True)

            lib_name_label = ctk.CTkLabel(
                left_stack,
                text=name,
                font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                text_color=COLOR_TEXT,
                anchor="w",
            )
            lib_name_label.pack(anchor="w")

            lib_desc_label = ctk.CTkLabel(
                left_stack,
                text=desc,
                font=ctk.CTkFont(family="Segoe UI", size=11),
                text_color=COLOR_TEXT_SECONDARY,
                anchor="w",
            )
            lib_desc_label.pack(anchor="w")

            license_badge = ctk.CTkLabel(
                row,
                text=license_str,
                font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
                fg_color=("#e2e8f0", "#1e293b"),
                text_color=COLOR_TEXT,
                corner_radius=4,
                padx=8,
                pady=2,
            )
            license_badge.pack(side="right")

        # Bottom padding inside credits card
        spacer = ctk.CTkLabel(self._credits_card, text="", height=10)
        spacer.pack()

        # 3. Privacy & Disclaimers Card
        self._notes_card = ctk.CTkFrame(
            self._scroll,
            fg_color=COLOR_CARD,
            corner_radius=10,
            border_width=1,
            border_color=COLOR_BORDER,
        )
        self._notes_card.pack(fill="x", padx=4, pady=(0, 20))

        notes_title = ctk.CTkLabel(
            self._notes_card,
            text="🔒   Privasi & Catatan Penggunaan",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color=COLOR_TEXT,
            anchor="w",
        )
        notes_title.pack(fill="x", padx=20, pady=(16, 8))

        notes = [
            ("🛡", "100% Pemrosesan Lokal (Privasi Terjamin)", "Aplikasi ini memproses semua gambar secara lokal di komputer Anda dan TIDAK PERNAH mengunggah gambar ke server internet manapun."),
            ("🤖", "Akurasi Model AI", "Hasil penghapusan background menggunakan deep learning AI dan mungkin tidak selalu sempurna, terutama jika warna foreground dan background sangat mirip."),
            ("💡", "Hak Cipta & Kreasi", "BG Remover MauL diciptakan dengan dedikasi untuk portofolio perangkat lunak berkualitas tinggi oleh MauL Studio."),
        ]

        for icon, title, note_text in notes:
            row = ctk.CTkFrame(self._notes_card, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=6)

            icon_lbl = ctk.CTkLabel(
                row,
                text=icon,
                font=ctk.CTkFont(size=16),
                width=24,
            )
            icon_lbl.pack(side="left", anchor="n", padx=(0, 8))

            text_stack = ctk.CTkFrame(row, fg_color="transparent")
            text_stack.pack(side="left", fill="x", expand=True)

            t_lbl = ctk.CTkLabel(
                text_stack,
                text=title,
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                text_color=COLOR_TEXT,
                anchor="w",
            )
            t_lbl.pack(anchor="w")

            d_lbl = ctk.CTkLabel(
                text_stack,
                text=note_text,
                font=ctk.CTkFont(family="Segoe UI", size=11),
                text_color=COLOR_TEXT_SECONDARY,
                anchor="w",
                justify="left",
                wraplength=660,
            )
            d_lbl.pack(anchor="w")

        spacer2 = ctk.CTkLabel(self._notes_card, text="", height=10)
        spacer2.pack()
