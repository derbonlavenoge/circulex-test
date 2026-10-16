"""Bande son de la vidéo 120 s : musique synthétisée (120 BPM), bruitages calés sur l'image,
voix off placée selon timeline.js, avec ducking de la musique sous la voix.

Usage : python3 audio.py <dossier_voix l01..l16.wav> <sfx.json> <sortie.wav>
(numpy uniquement, pas de scipy)
"""
import json, sys, wave, os
import numpy as np

SR = 44100
DUR = 120.0
N = int(SR * DUR)
HERE = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(7)


def read_wav(p):
    with wave.open(p) as w:
        assert w.getsampwidth() == 2 and w.getframerate() == SR
        x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64) / 32768
        if w.getnchannels() == 2:
            x = x.reshape(-1, 2).mean(1)
    return x


def add(buf, sig, t, gain=1.0):
    i = int(t * SR)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(sig))
    buf[max(i, 0):j] += gain * sig[max(0, -i):j - i]


def env(n, a=0.005, r=None):
    e = np.ones(n)
    na = max(1, int(a * SR))
    e[:na] = np.linspace(0, 1, na)
    if r:
        e *= np.exp(-np.arange(n) / (r * SR))
    return e


def lp_fast(x, k, passes=1):  # passe-bas vectorisé approx. (moyenne glissante)
    w = max(1, int(1 / k))
    for _ in range(passes):
        c = np.cumsum(np.concatenate([np.zeros(w // 2 + 1), x, np.zeros(w - w // 2)]))
        x = (c[w:w + len(x)] - c[:len(x)]) / w
    return x


def tone(freq, dur, kind='sine'):
    t = np.arange(int(dur * SR)) / SR
    ph = 2 * np.pi * np.cumsum(np.broadcast_to(freq, t.shape)) / SR if np.ndim(freq) else 2 * np.pi * freq * t
    if kind == 'sine':
        return np.sin(ph)
    if kind == 'tri':
        return 2 / np.pi * np.arcsin(np.sin(ph))
    if kind == 'soft':
        return np.sin(ph) + .35 * np.sin(2 * ph) + .15 * np.sin(3 * ph)
    raise ValueError(kind)


def note(m):
    return 440 * 2 ** ((m - 69) / 12)

# ------------------------------------------------------------------ musique
BEAT = 0.5; BAR = 2.0
PROG_A = [(57, [57, 60, 64]), (53, [53, 57, 60]), (48, [48, 52, 55]), (55, [55, 59, 62])]   # Am F C G
PROG_B = [(53, [53, 57, 60]), (48, [48, 52, 55]), (55, [55, 59, 62]), (57, [57, 60, 64])]   # F C G Am


def section(t):
    if t < 4: return 'intro'
    if t < 49: return 'A'
    if t < 78: return 'B'
    if t < 96: return 'light'
    if t < 114.5: return 'A2'
    return 'outro'


music = np.zeros(N)
drums = np.zeros(N)
nbars = int(DUR / BAR)
for b in range(nbars):
    t0 = b * BAR
    sec = section(t0 + .01)
    prog = PROG_B if sec == 'B' else PROG_A
    root, chord = prog[b % 4]
    if sec == 'outro':
        root, chord = 57, [57, 60, 64]
    # nappe
    pad = sum(tone(note(m + 12) * (1 + d), BAR + .3, 'soft') for m in chord for d in (-.002, .002))
    pe = np.minimum(1, np.arange(len(pad)) / (.25 * SR)) * np.minimum(1, (len(pad) - np.arange(len(pad))) / (.3 * SR))
    add(music, pad * pe * .045, t0)
    # arpège (croches)
    if sec != 'light':
        seq = chord + [chord[1] + 12] if sec != 'B' else [chord[0] + 12, chord[2], chord[1] + 12, chord[2] + 12]
        step = BEAT / 2
        for k in range(8):
            if sec == 'intro' and k % 2: continue
            m = seq[k % len(seq)] + 12
            s = tone(note(m), .4, 'sine') * env(int(.4 * SR), .003, .12)
            add(music, s * (.05 if sec != 'outro' else .03), t0 + k * step)
    if sec in ('intro', 'outro'):
        continue
    # basse
    for k in (0, 1.5, 2, 3):
        if sec == 'light' and k in (1.5, 3): continue
        s = tone(note(root - 12), .45, 'tri') * env(int(.45 * SR), .004, .18)
        add(music, s * .16, t0 + k * BEAT)
    # kick
    for k in range(4):
        if sec == 'light' and k % 2: continue
        n = int(.35 * SR); tt = np.arange(n) / SR
        f = 45 + 80 * np.exp(-tt * 28)
        s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 9)
        add(drums, s * .32, t0 + k * BEAT)
    # charleston
    if sec != 'light':
        hits = [k + .5 for k in range(4)] if sec != 'B' else [k * .5 + .25 for k in range(8)]
        for k in hits:
            n = int(.06 * SR); nz = rng.standard_normal(n); nz = np.diff(nz, prepend=0)
            add(drums, nz * env(n, .001, .015) * (.05 if sec != 'B' else .035), t0 + k * BEAT)

music += drums
# fondu final
music[-int(2.5 * SR):] *= np.linspace(1, 0, int(2.5 * SR)) ** 1.5
music[:int(.5 * SR)] *= np.linspace(0, 1, int(.5 * SR))

# ------------------------------------------------------------------ voix
tl = json.loads(open(os.path.join(HERE, 'timeline.js')).read().split('=', 1)[1].rstrip().rstrip(';'))
voice = np.zeros(N)
speech = np.zeros(N)
for L in tl:
    x = read_wav(os.path.join(sys.argv[1], f"l{L['i']:02d}.wav"))
    x = x / (np.max(np.abs(x)) + 1e-9) * .92
    add(voice, x, L['start'])
    i, j = int(L['start'] * SR), int((L['start'] + L['dur']) * SR)
    speech[i:j] = 1
# ducking : gain musique 1 hors voix, 0.4 sous la voix (rampes douces)
duck = 1 - .6 * lp_fast(speech, 1 / (.18 * SR), passes=2)

# ------------------------------------------------------------------ bruitages
fx = np.zeros(N)


def s_pop(v):
    n = int(.09 * SR); tt = np.arange(n) / SR
    f = 620 + 500 * tt / .09
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, .002, .03) * .5


def s_plop(v):
    n = int(.12 * SR); tt = np.arange(n) / SR
    f = 950 * np.exp(-tt * 18) + 260
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, .001, .04) * .55


def s_bubbles(v):
    out = np.zeros(int(1.3 * SR))
    for k in range(14):
        tk = rng.uniform(0, 1.15); f0 = rng.uniform(500, 1100) * (1 + tk * .6)
        n = int(.05 * SR); tt = np.arange(n) / SR
        b = np.sin(2 * np.pi * np.cumsum(f0 * (1 + 8 * tt)) / SR) * env(n, .002, .015)
        i = int(tk * SR); out[i:i + n] += b * rng.uniform(.15, .3)
    return out


def s_gloup(v):
    n = int(.22 * SR); tt = np.arange(n) / SR
    f = 320 * np.exp(-tt * 7) + 90 + 25 * np.sin(2 * np.pi * 22 * tt)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, .01, .08) * .7


def noise_burst(dur, a, r, smooth):
    n = int(dur * SR); nz = rng.standard_normal(n)
    nz = nz - lp_fast(nz, 1 / smooth)
    return nz * env(n, a, r)


def s_swish(v):
    s = noise_burst(.28, .06, .08, 6); return s * .35


def s_whoosh(v):
    n = int(.5 * SR); nz = rng.standard_normal(n)
    nz = lp_fast(nz, 1 / 3)
    e = np.sin(np.pi * np.arange(n) / n) ** 2
    return nz * e * .22


def s_tick(v):
    n = int(.03 * SR); tt = np.arange(n) / SR
    return np.sin(2 * np.pi * 2300 * tt) * env(n, .0005, .006) * .45


def s_tock(v):
    n = int(.03 * SR); tt = np.arange(n) / SR
    return np.sin(2 * np.pi * 1700 * tt) * env(n, .0005, .006) * .45


def s_chime(v):
    n = int(2.0 * SR); tt = np.arange(n) / SR
    s = sum(a * np.sin(2 * np.pi * f * tt) * np.exp(-tt * d) for f, a, d in
            ((1318.5, .5, 2.2), (1975.5, .3, 3), (2637, .2, 4), (659.3, .25, 1.6)))
    return s * env(n, .002) * .45


def s_stamp(v):
    n = int(.25 * SR); tt = np.arange(n) / SR
    f = 50 + 90 * np.exp(-tt * 30)
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 14) * .8 + noise_burst(.25, .001, .03, 4) * .25)


def s_buzz(v):
    n = int(.35 * SR); tt = np.arange(n) / SR
    s = np.sign(np.sin(2 * np.pi * 110 * tt)) * (0.6 + .4 * np.sin(2 * np.pi * 18 * tt))
    return lp_fast(s, 1 / 8) * env(n, .01, .15) * .2


def s_fizz(v):
    n = int(.7 * SR); out = np.zeros(n)
    for k in range(60):
        i = rng.integers(0, n - 200); out[i:i + 200] += rng.standard_normal(200) * env(200, .0002, .0008) * .3
    return out * np.linspace(1, .3, n)


SYN = dict(pop=s_pop, plop=s_plop, bubbles=s_bubbles, gloup=s_gloup, swish=s_swish, whoosh=s_whoosh,
           tick=s_tick, chime=s_chime, stamp=s_stamp, buzz=s_buzz, fizz=s_fizz)
ticks = 0
for e in json.load(open(sys.argv[2])):
    if e['type'] == 'tick':
        sig = (s_tick if ticks % 2 == 0 else s_tock)(1); ticks += 1
    else:
        sig = SYN[e['type']](e['v'])
    add(fx, sig, e['t'], e['v'])

# ------------------------------------------------------------------ mix
mix = voice * 1.0 + music * duck * .55 + fx * .5
mix = np.tanh(mix * 1.1) / np.tanh(1.1)
mix = mix / np.max(np.abs(mix)) * .95
st = np.stack([mix, mix], 1)
with wave.open(sys.argv[3], 'w') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((st * 32767).astype(np.int16).tobytes())
print('ok', len(mix) / SR, 's')
