"""Musique provisoire + effets sonores synchronisés avec render/stage.html.

Tout est synthétisé localement (aucun échantillon tiers) : la musique est une
maquette à remplacer par une piste instrumentale sous licence.
Usage : python3 audio/make_audio.py  → audio/music.wav, audio/sfx.wav
"""
import numpy as np, wave, os

SR = 44100
DUR = 90.0
N = int(SR * DUR)
HERE = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(7)


def save(name, x):
    x = np.clip(x, -1, 1)
    st = x if x.ndim == 2 else np.stack([x, x], 1)
    with wave.open(os.path.join(HERE, name), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((st * 32767).astype(np.int16).tobytes())


def env(n, a, r):
    e = np.ones(n)
    na, nr = int(a * SR), int(r * SR)
    if na: e[:na] = np.linspace(0, 1, na)
    if nr: e[-nr:] *= np.linspace(1, 0, nr) ** 2
    return e


def onepole_lp(x, fc):
    a = np.exp(-2 * np.pi * fc / SR); y = np.empty_like(x); s = 0.0
    for i, v in enumerate(x):
        s = (1 - a) * v + a * s; y[i] = s
    return y


def place(buf, sig, t, gain=1.0, pan=0.0):
    i = int(t * SR); j = min(len(buf), i + len(sig))
    if i >= len(buf): return
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    buf[i:j, 0] += sig[: j - i] * gain * l * 1.414
    buf[i:j, 1] += sig[: j - i] * gain * r * 1.414


def hz(m): return 440 * 2 ** ((m - 69) / 12)

# ------------------------------------------------------------------ musique
BPM = 100; BEAT = 60 / BPM; BAR = 4 * BEAT
# Do – Sol – Lam – Fa (I–V–vi–IV), voicings doux
CHORDS = [[48, 55, 64, 67, 72], [43, 55, 62, 67, 71], [45, 57, 64, 69, 72], [41, 53, 60, 65, 69]]
music = np.zeros((N, 2))


def pad_note(m, d):
    n = int(d * SR); t = np.arange(n) / SR; f = hz(m)
    x = sum(np.sin(2 * np.pi * f * k * (1 + dt) * t) / k ** 1.6 for k, dt in [(1, 0), (2, .0007), (3, -.0005), (4, .0004)])
    x += .5 * np.sin(2 * np.pi * f * 1.003 * t)
    return x * env(n, d * .35, d * .3) * .05


def pluck(m, d=.9):
    n = int(d * SR); t = np.arange(n) / SR; f = hz(m)
    x = np.sin(2 * np.pi * f * t) + .35 * np.sin(4 * np.pi * f * t) + .12 * np.sin(6 * np.pi * f * t)
    return x * np.exp(-t * 5.5) * env(n, .004, .05) * .09


def energy(t):
    """Intensité de l'arrangement selon la scène."""
    if t < 8: return 0
    if t < 18: return 1
    if t < 48: return 2
    if t < 60: return 1   # parents : plus intime
    if t < 84: return 2
    return 0

bar = 0; t = 0.0
while t < DUR:
    ch = CHORDS[bar % 4]
    for m in ch: place(music, pad_note(m, BAR * 1.15), t, .9, pan=(m % 5 - 2) * .15)
    place(music, pad_note(ch[0] - 12, BAR * 1.1), t, 1.4)
    e = energy(t + .01)
    if e >= 1:   # arpège
        pat = [ch[2] + 12, ch[3] + 12, ch[4] + 12, ch[3] + 12]
        for k in range(8):
            place(music, pluck(pat[k % 4] + (12 if k == 6 and e == 2 else 0)), t + k * BEAT / 2, 1.0 if e == 2 else .7, pan=.35 if k % 2 else -.35)
    if e == 2:   # pulsation légère (shaker + pied feutré)
        for k in range(8):
            n = int(.06 * SR); sh = rng.standard_normal(n) * np.exp(-np.arange(n) / SR * 70)
            sh = np.diff(np.concatenate([[0], sh]))
            place(music, sh * .05 * (1.0 if k % 2 else .55), t + k * BEAT / 2, pan=.25)
        for k in (0, 2):
            n = int(.25 * SR); tt = np.arange(n) / SR
            kick = np.sin(2 * np.pi * (55 + 60 * np.exp(-tt * 30)) * tt) * np.exp(-tt * 14) * .22
            place(music, kick, t + k * BEAT)
    bar += 1; t += BAR

# accord final qui résonne
for m in CHORDS[0] + [36]:
    place(music, pad_note(m, 6.5), 84.0, 1.1)
music[:, 0] = onepole_lp(music[:, 0], 5200); music[:, 1] = onepole_lp(music[:, 1], 5200)
fade = np.ones(N); fade[: int(1.5 * SR)] = np.linspace(0, 1, int(1.5 * SR)); fade[-int(2.5 * SR):] = np.linspace(1, 0, int(2.5 * SR))
music *= fade[:, None]
music /= np.abs(music).max() / .5
save("music.wav", music)

# ------------------------------------------------------------------ effets
sfx = np.zeros((N, 2))


def whoosh(d=.7, up=True):
    n = int(d * SR); t = np.arange(n) / SR
    x = rng.standard_normal(n)
    fc = np.linspace(400, 5000, n) if up else np.linspace(5000, 400, n)
    y = np.empty(n); s = 0.0
    for i in range(n):
        a = np.exp(-2 * np.pi * fc[i] / SR); s = (1 - a) * x[i] + a * s; y[i] = s
    shape = np.sin(np.pi * np.linspace(0, 1, n)) ** 2
    return y * shape * 1.6


def click():
    n = int(.03 * SR); t = np.arange(n) / SR
    return (rng.standard_normal(n) * .5 + np.sin(2 * np.pi * 2400 * t)) * np.exp(-t * 260) * .5


def key():
    n = int(.025 * SR); t = np.arange(n) / SR
    return np.diff(np.concatenate([[0], rng.standard_normal(n)])) * np.exp(-t * 300) * .18


def pop(f=660):
    n = int(.18 * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * f * (1 + .5 * np.exp(-t * 40)) * t) * np.exp(-t * 22) * .45


def chime(notes=(76, 83), gap=.09, d=1.2):
    out = np.zeros(int((d + gap * len(notes)) * SR))
    for k, m in enumerate(notes):
        n = int(d * SR); t = np.arange(n) / SR; f = hz(m)
        s = (np.sin(2 * np.pi * f * t) + .3 * np.sin(2 * np.pi * f * 2.01 * t)) * np.exp(-t * 4) * .3
        i = int(k * gap * SR); out[i:i + n] += s
    return out


def riser(d=1.2):
    n = int(d * SR); t = np.arange(n) / SR
    f = 200 + 900 * (t / d) ** 2
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * .2 + whoosh(d) * .5) * (t / d) ** 1.5


def soft_err():
    n = int(.35 * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 330 * t) + np.sin(2 * np.pi * 311 * t)) * np.exp(-t * 9) * .18


def tick():
    n = int(.08 * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * 1800 * t) * np.exp(-t * 60) * .18

# frappe clavier pendant la saisie du code (0,5 → 3,9 s)
t = .5
while t < 3.9:
    place(sfx, key(), t, rng.uniform(.6, 1.0), pan=rng.uniform(-.3, .3)); t += rng.uniform(.045, .11)
# autres passages de code tapé (scènes 3 et 4)
for a_, b_ in ((20.0, 20.9), (21.0, 22.9), (32.1, 33.2), (37.2, 37.85), (38.6, 39.5)):
    t = a_
    while t < b_:
        place(sfx, key(), t, rng.uniform(.5, .85), pan=rng.uniform(-.3, .3)); t += rng.uniform(.05, .1)
place(sfx, chime((79,), 0, .7), 21.2, .3); place(sfx, chime((83,), 0, .7), 23.2, .3)
place(sfx, soft_err(), 37.9, .6)
place(sfx, chime((72, 79, 84), .12, 1.6), 4.0, .6)          # dessin Turtle
for i, tt in enumerate((5.1, 5.55, 6.0)): place(sfx, pop(520 + i * 120), tt, .5)
for T in (8, 18, 48, 60, 84): place(sfx, whoosh(.85), T - .5, .55)
for T in (29.6, 75.6): place(sfx, whoosh(.9, up=False), T - .1, .3)
place(sfx, riser(1.1), 7.2, .35); place(sfx, chime((72, 76, 79, 84), .07, 2.2), 8.6, .55)  # logo
place(sfx, whoosh(.9), 11.3, .35)                            # navigateur
place(sfx, click(), 14.75, .6)                              # ouverture d'une séance
place(sfx, pop(600), 18.4, .7); place(sfx, pop(720), 19.4, .7)
for i, tt in enumerate((24.8, 26.0, 27.4, 28.6)): place(sfx, pop(523 * 2 ** (i * 4 / 12)), tt, .6)
for tt in (30.6, 34.4, 38.6, 42.6): place(sfx, tick(), tt, .8)
place(sfx, click(), 33.4, .7); place(sfx, chime((79,), 0, .8), 33.7, .45)   # Exécuter → sortie
place(sfx, soft_err(), 34.6, .8)                            # message d'erreur (doux)
place(sfx, click(), 39.6, .7); place(sfx, chime((72, 76, 79), .08, 1.4), 39.9, .55)  # Soumettre → réussi
place(sfx, chime((79, 84), .1, 1.4), 42.2, .35)             # Turtle
place(sfx, pop(880), 44.9, .4)                               # sauvegarde
for tt in (52.2, 53.6, 56.0): place(sfx, pop(660), tt, .55)
for tt in (60.6, 66.8, 70.4): place(sfx, tick(), tt, .8)
place(sfx, whoosh(.6), 69.8, .3); place(sfx, pop(990), 71.0, .35)   # zoom + loupe
for i in range(4): place(sfx, pop(560 + i * 90), 76.2 + i * .35, .45)
place(sfx, chime((76, 83), .1, 1.4), 79.5, .3); place(sfx, chime((79, 88), .1, 1.6), 81.7, .3)
place(sfx, chime((60, 67, 72, 76, 79), .06, 3.5), 84.4, .5); place(sfx, pop(780), 86.7, .5)
sfx /= max(1, np.abs(sfx).max() / .8)
save("sfx.wav", sfx)
print("ok")
