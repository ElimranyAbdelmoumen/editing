"""Placement d'une voix off sur la timeline et recalage des sous-titres.

Partagé par make_voice.py (voix de synthèse locale) et place_voice.py (prises
par scène, par ex. la voix clonée Higgsfield).
"""
import json, os, subprocess
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DUR = 90.0


def cues():
    m = json.loads(subprocess.check_output(["node", "-e",
        "import('./render/cues.js').then(m=>console.log(JSON.stringify(m)))"], cwd=ROOT))
    return m["SCENES"], m["SUBS"]


def scene_subs(sc, subs):
    """Indices des sous-titres de la scène, textes, début et fin de la fenêtre de voix."""
    idx = [i for i, c in enumerate(subs) if sc["t0"] <= c[0] < sc["t1"]]
    if not idx: return None
    return idx, [subs[i][2].replace("\n", " ") for i in idx], subs[idx[0]][0], subs[idx[-1]][1]


def trim(x, sr):
    env = np.abs(x) > max(.02, np.abs(x).max() * .03)
    i, j = np.argmax(env), len(env) - np.argmax(env[::-1])
    return x[max(0, i - int(.03 * sr)): j + int(.08 * sr)]


def tighten(x, sr, keep=.35):
    """Raccourcit les silences internes à `keep` secondes (débit fluide, sans accélérer la voix)."""
    hop = int(.01 * sr)
    e = np.array([np.sqrt(np.mean(x[k:k + hop] ** 2)) for k in range(0, len(x) - hop, hop)])
    quiet = e < max(.006, e.max() * .03)
    out, k, last = [], 0, 0
    while k < len(quiet):
        if quiet[k]:
            j = k
            while j < len(quiet) and quiet[j]: j += 1
            if (j - k) * .01 > keep and k > 0 and j < len(quiet):
                h = int(keep / 2 * sr)
                out.append(x[last:k * hop + h]); last = j * hop - h
            k = j
        else: k += 1
    out.append(x[last:])
    return np.concatenate(out)


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


def retime(x, sr, start, parts, idx, timed):
    """Sous-titres : estimation au prorata des caractères, accrochée à la pause la plus proche."""
    d = len(x) / sr
    ps = pauses(x, sr)
    total = sum(len(p) for p in parts)
    acc, bounds = 0, [0.0]
    for p in parts[:-1]:
        acc += len(p) + 1
        est = d * acc / (total + len(parts) - 1)
        near = min(ps, key=lambda q: abs(q - est)) if ps else est
        b = near if abs(near - est) < .7 else est
        bounds.append(b if b > bounds[-1] + .4 else max(est, bounds[-1] + .4))
    bounds.append(d)
    for k, i in enumerate(idx):
        timed[i] = [round(start + bounds[k] - (.05 if k == 0 else 0), 2),
                    round(start + bounds[k + 1] + (.15 if k == len(idx) - 1 else -.02), 2)]


def write(track, sr, timed):
    import wave
    track = track / max(1e-6, np.abs(track).max() / .9)
    os.makedirs(os.path.join(ROOT, "assets/voix"), exist_ok=True)
    with wave.open(os.path.join(ROOT, "assets/voix/voix_off.wav"), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((track * 32767).astype(np.int16).tobytes())
    json.dump(timed, open(os.path.join(ROOT, "render/subs_timed.json"), "w"))
