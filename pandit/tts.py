"""F2 open voice: Kokoro-82M (Apache-2.0) -> WAV -> MP3 (mono, 64 kbps) via ffmpeg.

ponytail: no Piper fallback yet; add it if Kokoro ever fails on the runner.
"""
import os
import subprocess

import numpy as np
import soundfile as sf

VOICE = os.environ.get("PANDIT_VOICE", "bm_george")  # British male; try bf_emma, am_michael
RATE = 24000


def speak(text, mp3_path):
    """Returns duration in seconds."""
    from kokoro import KPipeline
    pipe = KPipeline(lang_code=VOICE[0], repo_id="hexgrad/Kokoro-82M")
    audio = np.concatenate([a for _, _, a in pipe(text, voice=VOICE, speed=1.0)])
    wav = str(mp3_path).replace(".mp3", ".wav")
    sf.write(wav, audio, RATE)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-ac", "1", "-b:a", "64k", str(mp3_path)],
                   check=True)
    os.remove(wav)
    return round(len(audio) / RATE)
