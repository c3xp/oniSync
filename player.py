import os
import tempfile
from typing import Optional

import numpy as np
import simpleaudio as sa
import soundfile as sf


class AudioPlayer:
    def __init__(self) -> None:
        self.play_obj: Optional[sa.PlayObject] = None
        self.preview_temp_path: Optional[str] = None

    def play_preview(self, audio: np.ndarray, sample_rate: int) -> None:
        self.stop()

        temp_fd, temp_path = tempfile.mkstemp(prefix="onisync_preview_", suffix=".wav")
        os.close(temp_fd)

        sf.write(temp_path, audio, sample_rate)
        wave_obj = sa.WaveObject.from_wave_file(temp_path)

        self.preview_temp_path = temp_path
        self.play_obj = wave_obj.play()

    def stop(self) -> None:
        if self.play_obj is not None:
            try:
                self.play_obj.stop()
            except Exception:
                pass
            self.play_obj = None

        if self.preview_temp_path and os.path.exists(self.preview_temp_path):
            try:
                os.remove(self.preview_temp_path)
            except Exception:
                pass
            self.preview_temp_path = None
