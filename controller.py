import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

import numpy as np

from audio_engine import AudioEngine, AudioFileData
from player import AudioPlayer
from ui import BPMToolUI
from utils import format_duration, parse_positive_float


class BPMToolController:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.ui = BPMToolUI(root)
        self.audio_engine = AudioEngine()
        self.player = AudioPlayer()

        self.file_data: AudioFileData | None = None
        self.detected_bpm: float | None = None
        self.source_bpm_used: float | None = None

        self.converted_audio_cache: np.ndarray | None = None
        self.converted_cache_key: tuple[float, float] | None = None

        self._bind_events()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _bind_events(self) -> None:
        self.ui.open_button.configure(command=self.open_file)
        self.ui.analyze_button.configure(command=self.analyze_bpm)
        self.ui.halve_button.configure(command=self.halve_bpm)
        self.ui.double_button.configure(command=self.double_bpm)
        self.ui.set_manual_button.configure(command=self.set_manual_bpm)
        self.ui.preview_button.configure(command=self.preview_converted)
        self.ui.stop_button.configure(command=self.stop_preview)
        self.ui.export_button.configure(command=self.export_converted)

    def open_file(self) -> None:
        path = filedialog.askopenfilename(
            title="Seleziona un file audio",
            filetypes=[
                ("File audio", "*.wav *.mp3 *.flac *.ogg *.m4a *.aac"),
                ("Tutti i file", "*.*"),
            ],
        )
        if not path:
            return

        self.stop_preview()

        try:
            self.file_data = self.audio_engine.load_audio(path)
        except Exception as exc:
            messagebox.showerror("Errore apertura file", f"Impossibile aprire il file audio.\n\n{exc}")
            return

        self.detected_bpm = None
        self.source_bpm_used = None
        self.converted_audio_cache = None
        self.converted_cache_key = None

        self.ui.file_label_var.set(path)
        self.ui.duration_var.set(format_duration(self.file_data.duration_seconds))
        self.ui.sample_rate_var.set(f"{self.file_data.sample_rate} Hz")
        self.ui.detected_bpm_var.set("-")
        self.ui.source_bpm_var.set("-")
        self.ui.manual_bpm_var.set("")
        self.ui.set_status("File caricato. Premi 'Analizza BPM'.")

    def analyze_bpm(self) -> None:
        if self.file_data is None:
            messagebox.showwarning("Nessun file", "Prima seleziona un file audio.")
            return

        def worker() -> None:
            self.root.after(0, lambda: self.ui.set_busy(True, "Analisi BPM in corso...", "Step 1/3 • Preparazione audio"))
            try:
                self.root.after(0, lambda: self.ui.set_progress_text("Step 2/3 • Analisi transienti e onset"))
                bpm = self.audio_engine.detect_bpm(self.file_data.audio, self.file_data.sample_rate)
                self.detected_bpm = bpm
                self.source_bpm_used = bpm
                self.converted_audio_cache = None
                self.converted_cache_key = None

                self.root.after(0, lambda: self.ui.set_progress_text("Step 3/3 • Finalizzazione risultato"))
                self.root.after(0, self._refresh_bpm_ui)
                self.root.after(0, lambda: self.ui.set_busy(False, "Analisi completata."))
            except Exception as exc:
                self.root.after(0, lambda: self.ui.set_busy(False, "Errore durante l'analisi BPM."))
                self.root.after(0, lambda: messagebox.showerror("Errore analisi BPM", str(exc)))

        threading.Thread(target=worker, daemon=True).start()

    def _refresh_bpm_ui(self) -> None:
        if self.detected_bpm is not None:
            self.ui.detected_bpm_var.set(f"{self.detected_bpm:.2f}")
        if self.source_bpm_used is not None:
            self.ui.source_bpm_var.set(f"{self.source_bpm_used:.2f}")
            self.ui.manual_bpm_var.set(f"{self.source_bpm_used:.2f}")

    def halve_bpm(self) -> None:
        if self.source_bpm_used is None:
            messagebox.showwarning("BPM mancanti", "Prima analizza i BPM.")
            return

        self.source_bpm_used /= 2.0
        self.converted_audio_cache = None
        self.converted_cache_key = None
        self.ui.source_bpm_var.set(f"{self.source_bpm_used:.2f}")
        self.ui.manual_bpm_var.set(f"{self.source_bpm_used:.2f}")
        self.ui.set_status("BPM sorgente dimezzati.")

    def double_bpm(self) -> None:
        if self.source_bpm_used is None:
            messagebox.showwarning("BPM mancanti", "Prima analizza i BPM.")
            return

        self.source_bpm_used *= 2.0
        self.converted_audio_cache = None
        self.converted_cache_key = None
        self.ui.source_bpm_var.set(f"{self.source_bpm_used:.2f}")
        self.ui.manual_bpm_var.set(f"{self.source_bpm_used:.2f}")
        self.ui.set_status("BPM sorgente raddoppiati.")

    def set_manual_bpm(self) -> None:
        if self.file_data is None:
            messagebox.showwarning("Nessun file", "Prima seleziona un file audio.")
            return

        try:
            bpm = parse_positive_float(self.ui.manual_bpm_var.get(), "BPM manuali")
        except ValueError as exc:
            messagebox.showerror("Valore non valido", str(exc))
            return

        self.source_bpm_used = bpm
        self.converted_audio_cache = None
        self.converted_cache_key = None
        self.ui.source_bpm_var.set(f"{self.source_bpm_used:.2f}")
        self.ui.set_status("BPM sorgente impostati manualmente.")

    def _get_target_bpm(self) -> float:
        return parse_positive_float(self.ui.target_bpm_var.get(), "Target BPM")

    def _get_or_build_converted_audio(self) -> np.ndarray:
        if self.file_data is None:
            raise ValueError("Nessun file audio caricato.")
        if self.source_bpm_used is None:
            raise ValueError("Prima analizza o imposta i BPM sorgente.")

        target_bpm = self._get_target_bpm()
        cache_key = (round(self.source_bpm_used, 6), round(target_bpm, 6))

        if self.converted_audio_cache is not None and self.converted_cache_key == cache_key:
            return self.converted_audio_cache

        converted = self.audio_engine.convert_bpm(
            self.file_data.audio,
            self.source_bpm_used,
            target_bpm,
        )

        self.converted_audio_cache = converted
        self.converted_cache_key = cache_key
        return converted

    def preview_converted(self) -> None:
        if self.file_data is None:
            messagebox.showwarning("Nessun file", "Prima seleziona un file audio.")
            return

        def worker() -> None:
            self.root.after(0, lambda: self.ui.set_busy(True, "Preparazione preview...", "Generazione preview temporanea"))
            try:
                converted = self._get_or_build_converted_audio()
                self.player.play_preview(converted, self.file_data.sample_rate)
                self.root.after(0, lambda: self.ui.set_busy(False, "Preview in riproduzione."))
            except Exception as exc:
                self.root.after(0, lambda: self.ui.set_busy(False, "Errore durante la preview."))
                self.root.after(0, lambda: messagebox.showerror("Errore preview", str(exc)))

        threading.Thread(target=worker, daemon=True).start()

    def stop_preview(self) -> None:
        self.player.stop()
        self.ui.set_status("Preview fermata.")

    def export_converted(self) -> None:
        if self.file_data is None:
            messagebox.showwarning("Nessun file", "Prima seleziona un file audio.")
            return
        if self.source_bpm_used is None:
            messagebox.showwarning("BPM mancanti", "Prima analizza o imposta i BPM sorgente.")
            return

        try:
            target_bpm = self._get_target_bpm()
        except ValueError as exc:
            messagebox.showerror("Target BPM non valido", str(exc))
            return

        base_name = os.path.splitext(os.path.basename(self.file_data.path))[0]
        suggested_name = f"{base_name}_{int(round(target_bpm))}bpm.wav"

        output_path = filedialog.asksaveasfilename(
            title="Esporta WAV convertito",
            defaultextension=".wav",
            initialfile=suggested_name,
            filetypes=[("WAV", "*.wav")],
        )
        if not output_path:
            return

        def worker() -> None:
            self.root.after(0, lambda: self.ui.set_busy(True, "Esportazione in corso...", "Scrittura file WAV"))
            try:
                converted = self._get_or_build_converted_audio()
                self.audio_engine.export_wav(output_path, converted, self.file_data.sample_rate)
                self.root.after(0, lambda: self.ui.set_busy(False, "Export completato."))
                self.root.after(0, lambda: messagebox.showinfo("Export completato", f"File esportato:\n{output_path}"))
            except Exception as exc:
                self.root.after(0, lambda: self.ui.set_busy(False, "Errore durante l'export."))
                self.root.after(0, lambda: messagebox.showerror("Errore export", str(exc)))

        threading.Thread(target=worker, daemon=True).start()

    def on_close(self) -> None:
        self.player.stop()
        self.root.destroy()
