import tkinter as tk
from tkinter import ttk
from pathlib import Path
from PIL import Image, ImageTk

class BPMToolUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("OniSync")
        self.root.geometry("860x720")
        self.root.minsize(820, 680)
        self.root.configure(bg="#0b0b12")

        self.logo_image = None
        self.logo_label = None

        self.file_label_var = tk.StringVar(value="Nessun file selezionato")
        self.duration_var = tk.StringVar(value="-")
        self.sample_rate_var = tk.StringVar(value="-")
        self.detected_bpm_var = tk.StringVar(value="-")
        self.source_bpm_var = tk.StringVar(value="-")
        self.manual_bpm_var = tk.StringVar()
        self.target_bpm_var = tk.StringVar(value="130")
        self.status_var = tk.StringVar(value="Pronto.")

        self.open_button = None
        self.analyze_button = None
        self.preview_button = None
        self.stop_button = None
        self.export_button = None
        self.halve_button = None
        self.double_button = None
        self.set_manual_button = None

        self.manual_bpm_entry = None
        self.target_bpm_entry = None
        self.progress = None

        self._configure_theme()
        self._build()

    def _configure_theme(self) -> None:
        style = ttk.Style()

        try:
            style.theme_use("clam")
        except Exception:
            pass

        bg = "#0b0b12"
        panel = "#131320"
        panel_2 = "#171729"
        border = "#2a2a3d"
        text = "#f2f2f7"
        subtext = "#a9acc7"
        accent = "#7c5cff"
        accent_2 = "#00d0ff"
        button_bg = "#1a1a2b"
        button_active = "#262640"
        entry_bg = "#10101a"

        style.configure(".", background=bg, foreground=text, font=("Segoe UI", 10))
        style.configure("TFrame", background=bg)
        style.configure("Card.TFrame", background=panel)
        style.configure("InnerCard.TFrame", background=panel_2)

        style.configure(
            "TLabel",
            background=bg,
            foreground=text,
        )
        style.configure(
            "Muted.TLabel",
            background=panel,
            foreground=subtext,
            font=("Segoe UI", 9),
        )
        style.configure(
            "Title.TLabel",
            background=bg,
            foreground=text,
            font=("Segoe UI", 20, "bold"),
        )
        style.configure(
            "SectionTitle.TLabel",
            background=panel,
            foreground=text,
            font=("Segoe UI", 11, "bold"),
        )
        style.configure(
            "Value.TLabel",
            background=panel_2,
            foreground=text,
            font=("Consolas", 12, "bold"),
        )
        style.configure(
            "InfoLabel.TLabel",
            background=panel_2,
            foreground=subtext,
            font=("Segoe UI", 9),
        )

        style.configure(
            "TLabelFrame",
            background=panel,
            foreground=text,
            borderwidth=1,
            relief="solid",
        )
        style.configure(
            "TLabelFrame.Label",
            background=panel,
            foreground=text,
            font=("Segoe UI", 10, "bold"),
        )

        style.configure(
            "TButton",
            background=button_bg,
            foreground=text,
            borderwidth=0,
            focusthickness=0,
            padding=(12, 8),
        )
        style.map(
            "TButton",
            background=[
                ("active", button_active),
                ("disabled", "#111119"),
            ],
            foreground=[
                ("disabled", "#6c6f86"),
            ],
        )

        style.configure(
            "Accent.TButton",
            background=accent,
            foreground="white",
            padding=(14, 9),
            borderwidth=0,
        )
        style.map(
            "Accent.TButton",
            background=[
                ("active", "#9378ff"),
                ("disabled", "#3b3166"),
            ],
            foreground=[
                ("disabled", "#c9c2e8"),
            ],
        )

        style.configure(
            "Danger.TButton",
            background="#2b1620",
            foreground="#ffb8cb",
            padding=(12, 8),
            borderwidth=0,
        )
        style.map(
            "Danger.TButton",
            background=[
                ("active", "#40212e"),
                ("disabled", "#171017"),
            ],
            foreground=[
                ("disabled", "#7f6470"),
            ],
        )

        style.configure(
            "TEntry",
            fieldbackground=entry_bg,
            background=entry_bg,
            foreground=text,
            bordercolor=border,
            lightcolor=border,
            darkcolor=border,
            insertcolor=text,
            padding=6,
        )

        style.configure(
            "Horizontal.TProgressbar",
            troughcolor="#14141f",
            background=accent_2,
            bordercolor="#14141f",
            lightcolor=accent_2,
            darkcolor=accent_2,
            thickness=10,
        )

    def _build(self) -> None:
        outer = ttk.Frame(self.root, padding=18, style="TFrame")
        outer.pack(fill="both", expand=True)

        header = ttk.Frame(outer, style="TFrame")
        header.pack(fill="x", pady=(0, 14))

        self._add_logo(header)

        title_block = ttk.Frame(header, style="TFrame")
        title_block.pack(fill="x")

        ttk.Label(title_block, text="OniSync", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            title_block,
            text="BPM analyzer + converter for hardware sampling workflows",
            style="Muted.TLabel",
        ).pack(anchor="w", pady=(2, 0))

        content = ttk.Frame(outer, style="TFrame")
        content.pack(fill="both", expand=True)

        top_row = ttk.Frame(content, style="TFrame")
        top_row.pack(fill="x", pady=(0, 12))

        self._build_file_card(top_row)
        self._build_info_card(top_row)

        middle_row = ttk.Frame(content, style="TFrame")
        middle_row.pack(fill="x", pady=(0, 12))

        self._build_bpm_card(middle_row)
        self._build_convert_card(middle_row)

        self._build_notes_card(content)

        bottom = ttk.Frame(outer, style="TFrame")
        bottom.pack(fill="x", pady=(14, 0))

        self.progress = ttk.Progressbar(bottom, mode="indeterminate", style="Horizontal.TProgressbar")
        self.progress.pack(fill="x", pady=(0, 8))

        ttk.Label(bottom, textvariable=self.status_var, style="Muted.TLabel").pack(anchor="w")

    def _build_file_card(self, parent: ttk.Frame) -> None:
        card = ttk.LabelFrame(parent, text="File", padding=14)
        card.pack(side="left", fill="both", expand=True, padx=(0, 6))

        ttk.Label(card, text="Traccia selezionata", style="SectionTitle.TLabel").pack(anchor="w", pady=(0, 8))
        ttk.Label(card, textvariable=self.file_label_var, wraplength=360, style="Muted.TLabel").pack(anchor="w")

        buttons = ttk.Frame(card, style="Card.TFrame")
        buttons.pack(fill="x", pady=(14, 0))

        self.open_button = ttk.Button(buttons, text="Apri file")
        self.open_button.pack(side="left")

        self.analyze_button = ttk.Button(buttons, text="Analizza BPM", style="Accent.TButton")
        self.analyze_button.pack(side="left", padx=(8, 0))

    def _build_info_card(self, parent: ttk.Frame) -> None:
        card = ttk.LabelFrame(parent, text="Info", padding=14)
        card.pack(side="left", fill="both", expand=True, padx=(6, 0))

        grid = ttk.Frame(card, style="Card.TFrame")
        grid.pack(fill="both", expand=True)

        self._info_box(grid, 0, 0, "Durata", self.duration_var)
        self._info_box(grid, 0, 1, "Sample Rate", self.sample_rate_var)
        self._info_box(grid, 1, 0, "BPM Rilevati", self.detected_bpm_var)
        self._info_box(grid, 1, 1, "BPM Sorgente", self.source_bpm_var)

        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

    def _build_bpm_card(self, parent: ttk.Frame) -> None:
        card = ttk.LabelFrame(parent, text="Correzione BPM", padding=14)
        card.pack(side="left", fill="both", expand=True, padx=(0, 6))

        top = ttk.Frame(card, style="Card.TFrame")
        top.pack(fill="x")

        self.halve_button = ttk.Button(top, text="/2")
        self.halve_button.pack(side="left")

        self.double_button = ttk.Button(top, text="x2")
        self.double_button.pack(side="left", padx=(8, 0))

        manual_row = ttk.Frame(card, style="Card.TFrame")
        manual_row.pack(fill="x", pady=(14, 0))

        ttk.Label(manual_row, text="BPM manuali", style="Muted.TLabel").pack(anchor="w", pady=(0, 6))

        input_row = ttk.Frame(manual_row, style="Card.TFrame")
        input_row.pack(fill="x")

        self.manual_bpm_entry = ttk.Entry(input_row, textvariable=self.manual_bpm_var, width=16)
        self.manual_bpm_entry.pack(side="left")

        self.set_manual_button = ttk.Button(input_row, text="Imposta")
        self.set_manual_button.pack(side="left", padx=(8, 0))

    def _build_convert_card(self, parent: ttk.Frame) -> None:
        card = ttk.LabelFrame(parent, text="Conversione", padding=14)
        card.pack(side="left", fill="both", expand=True, padx=(6, 0))

        ttk.Label(card, text="Target BPM", style="Muted.TLabel").pack(anchor="w", pady=(0, 6))

        self.target_bpm_entry = ttk.Entry(card, textvariable=self.target_bpm_var, width=16)
        self.target_bpm_entry.pack(anchor="w")

        buttons = ttk.Frame(card, style="Card.TFrame")
        buttons.pack(fill="x", pady=(14, 0))

        self.preview_button = ttk.Button(buttons, text="Preview", style="Accent.TButton")
        self.preview_button.pack(side="left")

        self.stop_button = ttk.Button(buttons, text="Stop", style="Danger.TButton")
        self.stop_button.pack(side="left", padx=(8, 0))

        self.export_button = ttk.Button(buttons, text="Esporta WAV")
        self.export_button.pack(side="left", padx=(8, 0))

    def _build_notes_card(self, parent: ttk.Frame) -> None:
        card = ttk.LabelFrame(parent, text="Workflow Notes", padding=14)
        card.pack(fill="both", expand=True)

        notes = (
            "• BPM detect può leggere metà o doppio tempo.\n"
            "• Se una traccia techno da 130 viene letta 65, premi x2.\n"
            "• La conversione prepara il file per sampler senza timestretch interno.\n"
            "• Tagli finali e loop perfetti: meglio rifinirli in Audacity."
        )

        ttk.Label(card, text=notes, wraplength=780, style="Muted.TLabel", justify="left").pack(anchor="w")

# ------------------------------

    def _add_logo(self, parent: ttk.Frame) -> None:
        logo_path = Path(__file__).resolve().parent / "assets" / "logo.png"
        if not logo_path.exists():
            return

        try:
            image = Image.open(logo_path).convert("RGBA")

            bbox = image.getbbox()
            if bbox:
                image = image.crop(bbox)

            max_width = 420
            max_height = 140

            image.thumbnail((max_width, max_height), Image.LANCZOS)

            self.logo_image = ImageTk.PhotoImage(image)
            self.logo_label = ttk.Label(parent, image=self.logo_image, background="#0b0b12")
            self.logo_label.pack(anchor="center", pady=(0, 14))

        except Exception:
            pass

# ------------------------------

    def _info_box(
        self,
        parent: ttk.Frame,
        row: int,
        column: int,
        title: str,
        value_var: tk.StringVar,
    ) -> None:
        box = ttk.Frame(parent, style="InnerCard.TFrame", padding=12)
        box.grid(row=row, column=column, sticky="nsew", padx=6, pady=6)

        ttk.Label(box, text=title, style="InfoLabel.TLabel").pack(anchor="w")
        ttk.Label(box, textvariable=value_var, style="Value.TLabel").pack(anchor="w", pady=(6, 0))

    def set_busy(self, busy: bool, status: str | None = None) -> None:
        state = "disabled" if busy else "normal"

        for widget in [
            self.open_button,
            self.analyze_button,
            self.preview_button,
            self.stop_button,
            self.export_button,
            self.halve_button,
            self.double_button,
            self.set_manual_button,
            self.manual_bpm_entry,
            self.target_bpm_entry,
        ]:
            widget.configure(state=state)

        if busy:
            self.progress.start(10)
        else:
            self.progress.stop()

        if status is not None:
            self.status_var.set(status)

    def set_status(self, text: str) -> None:
        self.status_var.set(text)
        self.root.update_idletasks()