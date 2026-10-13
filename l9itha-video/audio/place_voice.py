"""Voix off enregistrée ou clonée, une prise par scène.

Lit assets/voix/scenes/scene_<id>[suffixe].(wav|mp3|m4a|ogg) (id = scène de
render/cues.js ; plusieurs prises possibles, ex. scene_4.wav et scene_4_rapide.wav),
retire les silences de début et de fin, garde la prise la plus posée qui tient
dans sa fenêtre, l'accélère légèrement si besoin (max ×1,15, sans changer la
hauteur), la cale au début de sa fenêtre, puis écrit assets/voix/voix_off.wav
et render/subs_timed.json.
Usage : python3 audio/place_voice.py
"""
import glob, os, subprocess, sys
import numpy as np
from voice_layout import ROOT, DUR, cues, scene_subs, trim, tighten, retime, write

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
    files = [f for f in glob.glob(os.path.join(ROOT, f"assets/voix/scenes/scene_{sc['id']}*"))
             if os.path.basename(f).split(".")[0].split("_")[1] == str(sc["id"])]
    if not files: missing.append(sc["id"]); continue
    # la prise peut déborder dans le blanc avant la scène suivante (0,4 s gardées avant elle)
    nxt = [scene_subs(o, SUBS) for o in SCENES if o["t0"] >= sc["t1"]]
    nxt = [n[2] for n in nxt if n]
    window = (nxt[0] if nxt else DUR) - .4 - start
    takes = sorted(((tighten(trim(load(f), SR), SR), f) for f in files), key=lambda c: len(c[0]))
    fit = [c for c in takes if len(c[0]) / SR <= window * 1.15]
    x, f = fit[-1] if fit else takes[0]
    tempo = 1.0
    if len(x) / SR > window:
        tempo = min(1.15, len(x) / SR / window)
        x = tighten(trim(load(f, tempo), SR), SR)
    n = int(.015 * SR); x = x.copy(); x[:n] *= np.linspace(0, 1, n); x[-n:] *= np.linspace(1, 0, n)  # pas de clic aux raccords
    d = len(x) / SR
    flag = "  ⚠ déborde de la fenêtre" if d > window + .05 else ""
    i0 = int(start * SR); track[i0:i0 + len(x)] += x[: len(track) - i0]
    retime(x, SR, start, parts, idx, timed)
    print(f"scène {sc['id']}: {os.path.basename(f)} {d:4.1f}s / fenêtre {window:4.1f}s  tempo ×{tempo:.2f}{flag}")

if missing:
    sys.exit(f"Prises manquantes pour les scènes {missing} dans assets/voix/scenes/")
for a, b in zip(timed, timed[1:]):  # pas de chevauchement entre sous-titres
    if a and b and a[1] > b[0] - .02: a[1] = round(b[0] - .02, 2)
write(track, SR, timed)
print("ok")
