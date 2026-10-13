"""Voix off provisoire (synthèse locale, voix masculine française « tom »).

Génère assets/voix/voix_off.wav (90 s, calée sur la timeline) et
render/subs_timed.json (timings des sous-titres recalés sur les pauses réelles).
Modèle : vits-piper-fr_FR-tom-medium (sherpa-onnx), chemin via TTS_MODEL_DIR.
Usage : TTS_MODEL_DIR=/chemin/vits-piper-fr_FR-tom-medium python3 audio/make_voice.py
"""
import glob, os
import numpy as np
import sherpa_onnx
from voice_layout import DUR, cues, scene_subs, trim, retime, write

MODEL = os.environ.get("TTS_MODEL_DIR", "/tmp/claude-0/vits-piper-fr_FR-tom-medium")

# Prononciation : le nom s'écrit L9ITHA.Club mais se dit « Lqitha Club ».
SAY = {"L9ITHA.Club": "Lquita Club"}

SCENES, SUBS = cues()

tts = sherpa_onnx.OfflineTts(sherpa_onnx.OfflineTtsConfig(
    model=sherpa_onnx.OfflineTtsModelConfig(
        vits=sherpa_onnx.OfflineTtsVitsModelConfig(
            model=glob.glob(MODEL + "/*.onnx")[0], tokens=MODEL + "/tokens.txt",
            data_dir=MODEL + "/espeak-ng-data", length_scale=1.0),
        num_threads=4)))


def speak(text, speed):
    for a, b in SAY.items(): text = text.replace(a, b)
    a = tts.generate(text, sid=0, speed=speed)
    x = np.array(a.samples, dtype=np.float32)
    return trim(x, a.sample_rate), a.sample_rate


SR = None
track = None
timed = [None] * len(SUBS)
for sc in SCENES:
    s = scene_subs(sc, SUBS)
    if not s: continue
    idx, parts, start, end = s
    text = " ".join(parts)
    window = end - start
    x, sr = speak(text, 1.0)
    # débit posé : on vise ~90 % de la fenêtre (ralenti max 0,88, accéléré max 1,3)
    speed = float(np.clip(len(x) / sr / (window * .9), .88, 1.3))
    if abs(speed - 1) > .01: x, sr = speak(text, speed)
    if track is None: SR = sr; track = np.zeros(int(DUR * sr), dtype=np.float32)
    d = len(x) / sr
    i0 = int(start * sr); track[i0:i0 + len(x)] += x[: len(track) - i0]
    retime(x, sr, start, parts, idx, timed)
    print(f"scène {sc['id']}: {d:4.1f}s / fenêtre {window:4.1f}s  vitesse {speed:.2f}")

write(track, SR, timed)
print("ok")
