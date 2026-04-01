import math
from dataclasses import dataclass

import librosa
import numpy as np
import soundfile as sf


@dataclass
class AudioFileData:
    path: str
    audio: np.ndarray
    sample_rate: int
    duration_seconds: float


class AudioEngine:
    def load_audio(self, path: str) -> AudioFileData:
        audio, sr = librosa.load(path, sr=None, mono=True)
        audio = audio.astype(np.float32, copy=False)
        duration_seconds = float(len(audio) / sr)
        return AudioFileData(
            path=path,
            audio=audio,
            sample_rate=int(sr),
            duration_seconds=duration_seconds,
        )

    def detect_bpm(self, audio: np.ndarray, sample_rate: int) -> float:
        onset_env = librosa.onset.onset_strength(y=audio, sr=sample_rate)
        tempo = librosa.feature.tempo(
            onset_envelope=onset_env,
            sr=sample_rate,
            aggregate=np.median,
        )
        return float(tempo[0])

    def convert_bpm(self, audio: np.ndarray, source_bpm: float, target_bpm: float) -> np.ndarray:
        if source_bpm <= 0 or target_bpm <= 0:
            raise ValueError("I BPM devono essere maggiori di 0.")

        stretch_rate = target_bpm / source_bpm
        if not math.isfinite(stretch_rate) or stretch_rate <= 0:
            raise ValueError("Rate di conversione non valido.")

        converted = librosa.effects.time_stretch(audio, rate=stretch_rate)
        return np.clip(converted, -1.0, 1.0).astype(np.float32, copy=False)

    def export_wav(self, output_path: str, audio: np.ndarray, sample_rate: int) -> None:
        sf.write(output_path, audio, sample_rate)
