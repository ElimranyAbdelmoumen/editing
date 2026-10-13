"""Voix off enregistrée ou clonée, une prise par scène.

Lit assets/voix/scenes/scene_<id>.(wav|mp3|m4a|ogg) (id = scène de render/cues.js),
retire les silences de début et de fin, accélère légèrement une prise trop
longue pour sa fenêtre (max ×1,15, sans changer la hauteur), la cale au début
de sa fenêtre, puis écrit assets/voix/voix_off.wav et render/subs_timed.json.
Usage : python3 audio/place_voice.py
"""
import glob, os, subprocess, sys
import numpy as np
from voice_layout import ROOT, DUR, cues, scene_subs, trim, retime, write

SR = 44100
SCENES, SUBS = cues()


def load(path, tempo=1.0):
    af = ["-af", f"atempo={tempo:.4f}"] if abs(tempo - 1) > .005 else []
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", path, *af, "-ac", "1",
                                   "-ar", str(SR), "-f", "f32le", "-"])
    return np.frombuffer(raw, dtype=np.float32).copy()


track = np.zeros(int(DUR * SR), dtype=np.float32)
timed = [None] * len(SUBS)
missing = []
for sc in SCENES:
    s = scene_subs(sc, SUBS)
    if not s: continue
    idx, parts, start, end = s
    files = sorted(glob.glob(os.path.join(ROOT, f"assets/voix/scenes/scene_{sc['id']}.*")))
    if not files: missing.append(sc["id"]); continue
    window = end - start
    x = trim(load(files[0]), SR)
    tempo = 1.0
    if len(x) / SR > window:
        tempo = min(1.15, len(x) / SR / window)
        x = trim(load(files[0], tempo), SR)
    d = len(x) / SR
    flag = "  ⚠ déborde de la fenêtre" if d > window + .05 else ""
    i0 = int(start * SR); track[i0:i0 + len(x)] += x[: len(track) - i0]
    retime(x, SR, start, parts, idx, timed)
    print(f"scène {sc['id']}: {d:4.1f}s / fenêtre {window:4.1f}s  tempo ×{tempo:.2f}{flag}")

if missing:
    sys.exit(f"Prises manquantes pour les scènes {missing} dans assets/voix/scenes/")
write(track, SR, timed)
print("ok")
