"""Version « story » 9:16 : timeline, sous-titres mot à mot et mixage audio.

Entrées : story/assets/v1..v9.mp3 (voix « Julian »), story/script.json (texte).
Sorties : story/timeline.json (lu par story/stage.html) et story/out/mix.wav.
Les temps des mots viennent d'une transcription (faster-whisper) mise en cache
dans story/words.json ; sans ce fichier ni faster-whisper, répartition au prorata.
Usage : python3 story/make_story.py
"""
import difflib, json, os, re, subprocess, unicodedata, wave
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SR = 44100
LEAD, TAIL, MIN_DUR = .45, .55, 3.4
END_TAIL = 2.4  # la carte de fin reste à l'écran après la dernière phrase
rng = np.random.default_rng(3)
LINES = json.load(open(os.path.join(HERE, "script.json"), encoding="utf-8"))


def load(p):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", p, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"])
    return np.frombuffer(raw, np.float32).copy()


def bounds(x):
    """Début et fin de la parole (en échantillons)."""
    on = np.abs(x) > max(.01, np.abs(x).max() * .03)
    i, j = np.argmax(on), len(on) - np.argmax(on[::-1])
    return max(0, i - int(.02 * SR)), min(len(x), j + int(.06 * SR))


def norm(w):
    w = unicodedata.normalize("NFD", w.lower())
    return re.sub(r"[^a-z0-9]", "", "".join(c for c in w if unicodedata.category(c) != "Mn"))


def whisper_words():
    cache = os.path.join(HERE, "words.json")
    if os.path.exists(cache): return json.load(open(cache))
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        return None
    m = WhisperModel("small", device="cpu", compute_type="int8"); out = []
    for k in range(1, len(LINES) + 1):
        x = load(os.path.join(HERE, f"assets/v{k}.mp3"))
        x16 = x[::int(SR / 16000)] if SR % 16000 == 0 else np.interp(np.arange(0, len(x), SR / 16000), np.arange(len(x)), x).astype(np.float32)
        segs, _ = m.transcribe(x16, language="fr", word_timestamps=True)
        out.append([[w.word.strip(), round(w.start, 3), round(w.end, 3)] for s in segs for w in s.words])
    json.dump(out, open(cache, "w"), ensure_ascii=False)
    return out


def align(script, heard, t0, t1):
    """Temps de chaque mot du script, d'après les mots entendus (repli : prorata des lettres)."""
    words = []
    for w in script.split():  # ponctuation isolée (« : », « ? ») collée au mot précédent
        if words and not norm(w): words[-1] += "\u202f" + w
        else: words.append(w)
    times = [None] * len(words)
    if heard:
        sm = difflib.SequenceMatcher(a=[norm(w) for w in words], b=[norm(h[0]) for h in heard], autojunk=False)
        for blk in sm.get_matching_blocks():
            for k in range(blk.size): times[blk.a + k] = heard[blk.b + k][1:]
    # mots non reconnus : interpolation entre voisins connus, au prorata des lettres
    known = [(-1, (t0, t0))] + [(i, t) for i, t in enumerate(times) if t] + [(len(words), (t1, t1))]
    for (ia, ta), (ib, tb) in zip(known, known[1:]):
        if ib - ia <= 1: continue
        span = words[ia + 1: ib]; L = sum(len(w) for w in span); a, b = ta[1], tb[0]; acc = 0
        for k, w in enumerate(span):
            s = a + (b - a) * acc / L; acc += len(w); times[ia + 1 + k] = (s, a + (b - a) * acc / L)
    return [{"w": w, "s": round(t[0], 3), "e": round(t[1], 3)} for w, t in zip(words, times)]


# ------------------------------------------------------------------ timeline
heard = whisper_words()
scenes, voice_parts, t = [], [], 0.0
for k, line in enumerate(LINES, 1):
    x = load(os.path.join(HERE, f"assets/v{k}.mp3")); i, j = bounds(x); x = x[i:j]
    d = len(x) / SR
    dur = max(MIN_DUR, LEAD + d + (END_TAIL if k == len(LINES) else TAIL))
    h = [[w, s - i / SR, e - i / SR] for w, s, e in heard[k - 1]] if heard else None
    words = align(line, h, 0, d)
    for w in words: w["s"] = round(w["s"] + t + LEAD, 3); w["e"] = round(w["e"] + t + LEAD, 3)
    scenes.append({"id": k, "t0": round(t, 3), "t1": round(t + dur, 3), "words": words})
    voice_parts.append((t + LEAD, x)); t += dur
TOTAL = round(t, 3)
json.dump({"duration": TOTAL, "scenes": scenes}, open(os.path.join(HERE, "timeline.json"), "w"), ensure_ascii=False, indent=1)
print(f"durée {TOTAL:.1f} s :", " ".join(f"{s['id']}:{s['t1'] - s['t0']:.1f}" for s in scenes))

# ------------------------------------------------------------------ audio
N = int(TOTAL * SR) + SR
voice = np.zeros(N, np.float32)
for t0, x in voice_parts:
    i = int(t0 * SR); voice[i:i + len(x)] += x
sfx = np.zeros(N)


def place(sig, t, g=1.0):
    i = int(t * SR); voice_len = min(len(sig), N - i); sfx[i:i + voice_len] += sig[:voice_len] * g


def whoosh(d=.6, up=True):
    n = int(d * SR); x = rng.standard_normal(n)
    fc = np.linspace(500, 5500, n) if up else np.linspace(5500, 500, n)
    a = np.exp(-2 * np.pi * fc / SR); y = np.empty(n); s = 0.0
    for q in range(n): s = (1 - a[q]) * x[q] + a[q] * s; y[q] = s
    return y * np.sin(np.pi * np.linspace(0, 1, n)) ** 2 * 1.4


def key():
    n = int(.025 * SR); tt = np.arange(n) / SR
    return np.diff(np.concatenate([[0], rng.standard_normal(n)])) * np.exp(-tt * 300) * .18


def tone(f, d, decay, g):
    tt = np.arange(int(d * SR)) / SR
    return (np.sin(2 * np.pi * f * tt) + .3 * np.sin(2 * np.pi * f * 2.01 * tt)) * np.exp(-tt * decay) * g


S = {s["id"]: s for s in scenes}
for s in scenes[1:]: place(whoosh(.55, s["id"] % 2 == 0), s["t0"] - .3, .5)
tk = S[3]["t0"] + .5
while tk < S[3]["t0"] + 1.6: place(key(), tk, rng.uniform(.6, 1)); tk += rng.uniform(.05, .1)
place(tone(1568, .8, 5, .25), S[3]["t0"] + 1.75, 1)                         # « Bonjour ! »
place(tone(330, .35, 9, .2) + tone(311, .35, 9, .2), S[4]["t0"] + .7, 1)     # erreur douce
place(tone(988, .6, 6, .2), S[4]["t0"] + 1.6, 1)                             # indice
for q, f in enumerate((1047, 1319, 1568, 2093)): place(tone(f, 1.2, 3.5, .22), S[5]["t0"] + .15 + q * .09, 1)
place(tone(660, .25, 20, .4), S[6]["t0"] + 1.1, 1)                           # badge points
for q, f in enumerate((784, 988, 1175)): place(tone(f, 1.4, 3, .2), S[9]["t0"] + .9 + q * .12, 1)

out = os.path.join(HERE, "out"); os.makedirs(out, exist_ok=True)
for name, arr in (("voice.wav", voice), ("sfx.wav", sfx)):
    with wave.open(os.path.join(out, name), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(arr, -1, 1) * 32767).astype(np.int16).tobytes())
music = os.path.join(ROOT, "audio/music.wav")
if not os.path.exists(music): subprocess.check_call(["python3", os.path.join(ROOT, "audio/make_audio.py")])
subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-i", music, "-i", os.path.join(out, "sfx.wav"), "-i", os.path.join(out, "voice.wav"),
    "-filter_complex",
    f"[0:a]atrim=0:{TOTAL},afade=t=in:d=0.4,afade=t=out:st={TOTAL - 2.2}:d=2.2,volume=0.6[m0];"
    "[2:a]aresample=44100,highpass=f=70,acompressor=threshold=0.1:ratio=3:attack=10:release=150,aformat=channel_layouts=stereo,loudnorm=I=-16:TP=-1.5,asplit[vo][key];"
    "[m0][key]sidechaincompress=threshold=0.03:ratio=6:attack=30:release=400[md];"
    "[1:a]aformat=channel_layouts=stereo,volume=0.8[fx];[md][fx][vo]amix=inputs=3:normalize=0,alimiter=limit=0.95[a]",
    "-map", "[a]", "-t", str(TOTAL), "-c:a", "pcm_s16le", os.path.join(out, "mix.wav")])
print("ok")
