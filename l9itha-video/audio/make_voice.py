"""Voix off provisoire (synthèse locale, voix masculine française « tom »).

Génère assets/voix/voix_off.wav (90 s, calée sur la timeline) et
render/subs_timed.json (timings des sous-titres recalés sur les pauses réelles).
Modèle : vits-piper-fr_FR-tom-medium (sherpa-onnx), chemin via TTS_MODEL_DIR.
Usage : TTS_MODEL_DIR=/chemin/vits-piper-fr_FR-tom-medium python3 audio/make_voice.py
"""
import glob, json, os, subprocess, wave
import numpy as np
import sherpa_onnx

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL = os.environ.get("TTS_MODEL_DIR", "/tmp/claude-0/vits-piper-fr_FR-tom-medium")
DUR = 90.0

# Prononciation : le nom s'écrit L9ITHA.Club mais se dit « Lqitha Club ».
SAY = {"L9ITHA.Club": "Lquita Club"}

m = json.loads(subprocess.check_output(["node", "-e",
    "import('./render/cues.js').then(m=>console.log(JSON.stringify(m)))"], cwd=ROOT))
SCENES, SUBS = m["SCENES"], m["SUBS"]

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
    sr = a.sample_rate
    env = np.abs(x) > 0.02
    i, j = np.argmax(env), len(env) - np.argmax(env[::-1])
    return x[max(0, i - int(.03 * sr)): j + int(.08 * sr)], sr


def pauses(x, sr, min_len=.12):
    """Milieux des silences (en s) dans x."""
    hop = int(.01 * sr)
    e = np.array([np.sqrt(np.mean(x[k:k + hop] ** 2)) for k in range(0, len(x) - hop, hop)])
    quiet = e < max(.008, e.max() * .04)
    out, k = [], 0
    while k < len(quiet):
        if quiet[k]:
            j = k
            while j < len(quiet) and quiet[j]: j += 1
            if (j - k) * .01 >= min_len: out.append((k + j) / 2 * .01)
            k = j
        else: k += 1
    return out


SR = None
track = None
timed = [None] * len(SUBS)
for sc in SCENES:
    idx = [i for i, c in enumerate(SUBS) if sc["t0"] <= c[0] < sc["t1"]]
    if not idx: continue
    parts = [SUBS[i][2].replace("\n", " ") for i in idx]
    text = " ".join(parts)
    start, end = SUBS[idx[0]][0], SUBS[idx[-1]][1]
    window = end - start
    x, sr = speak(text, 1.0)
    # débit posé : on vise ~90 % de la fenêtre (ralenti max 0,88, accéléré max 1,3)
    speed = float(np.clip(len(x) / sr / (window * .9), .88, 1.3))
    if abs(speed - 1) > .01: x, sr = speak(text, speed)
    if track is None: SR = sr; track = np.zeros(int(DUR * sr), dtype=np.float32)
    d = len(x) / sr
    i0 = int(start * sr); track[i0:i0 + len(x)] += x[: len(track) - i0]
    # recalage des sous-titres : estimation au prorata des caractères, accrochée à la pause la plus proche
    ps = pauses(x, sr)
    total = sum(len(p) for p in parts)
    acc, bounds = 0, [0.0]
    for p in parts[:-1]:
        acc += len(p) + 1
        est = d * acc / (total + len(parts) - 1)
        near = min(ps, key=lambda q: abs(q - est)) if ps else est
        bounds.append(near if abs(near - est) < .7 else est)
    bounds.append(d)
    for k, i in enumerate(idx):
        timed[i] = [round(start + bounds[k] - (.05 if k == 0 else 0), 2), round(start + bounds[k + 1] + (.15 if k == len(idx) - 1 else -.02), 2)]
    print(f"scène {sc['id']}: {d:4.1f}s / fenêtre {window:4.1f}s  vitesse {speed:.2f}")

track /= max(1e-6, np.abs(track).max() / .9)
os.makedirs(os.path.join(ROOT, "assets/voix"), exist_ok=True)
with wave.open(os.path.join(ROOT, "assets/voix/voix_off.wav"), "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((track * 32767).astype(np.int16).tobytes())
json.dump(timed, open(os.path.join(ROOT, "render/subs_timed.json"), "w"))
print("ok")
