import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve
SR = 48000
def _bp(x, a, b): return sosfilt(butter(2, [a / (SR / 2), min(b, SR / 2 - 200) / (SR / 2)], 'band', output='sos'), x)
def _lp(x, f): return sosfilt(butter(2, f / (SR / 2), 'low', output='sos'), x)
def _hp(x, f): return sosfilt(butter(2, f / (SR / 2), 'high', output='sos'), x)
def midi(m): return 440 * 2 ** ((m - 69) / 12)
class Score:
    def __init__(s, N, seed=1): s.N = N; s.rs = np.random.RandomState(seed); s.dry = np.zeros(N); s.wet = np.zeros(N)
    def put(s, x, at, g=1.0, wet=0.0):
        i = int(at * SR)
        if i >= s.N or i + len(x) < 0: return
        if i < 0: x = x[-i:]; i = 0
        n = min(len(x), s.N - i); s.dry[i:i + n] += x[:n] * g * (1 - wet * .5); s.wet[i:i + n] += x[:n] * g * wet
    # ---- instruments
    def sub808(s, f, d=1.2, drive=1.6):
        n = int(d * SR); t = np.arange(n) / SR; ph = np.cumsum(f * (1 + 1.1 * np.exp(-t * 45))) / SR; x = np.tanh(np.sin(2 * np.pi * ph) * drive) * np.exp(-t * (2.6 / max(d, .3))) * np.minimum(t / .002, 1); return x
    def braam(s, f, d=3.0):
        n = int((d + 1.5) * SR); t = np.arange(n) / SR; x = np.zeros(n)
        for det in (-.012, -.004, 0, .004, .012):
            ff = f * (1 + det)
            for h in range(1, 14): x += np.sin(2 * np.pi * ff * h * t + s.rs.rand() * 6) / h ** 1.1
        x = _lp(x, 900) * 0.9; x += np.sin(2 * np.pi * f / 2 * t) * 1.2
        env = np.minimum(t / .08, 1) * np.where(t < d, 1, np.exp(-(t - d) * 2.4)) * (.5 + .5 * np.exp(-t * .9)); return np.tanh(x * env * .9) * .8
    def choir(s, f, d, att=.9, rel=1.4, voices=3):
        n = int((d + rel) * SR); t = np.arange(n) / SR; x = np.zeros(n)
        for v in range(voices):
            ff = f * (1 + (v - 1) * .004) * (1 + .004 * np.sin(2 * np.pi * (5.2 + v * .4) * t + v))
            ph = np.cumsum(ff) / SR * 2 * np.pi
            for h in range(1, 14):
                w = np.exp(-((h * f - 780) / 520) ** 2) + .7 * np.exp(-((h * f - 1250) / 640) ** 2) + .05
                x += np.sin(ph * h) * w / h ** .5
        env = np.minimum(t / att, 1) ** 1.4 * np.where(t < d, 1, np.exp(-(t - d) / (rel / 3.5))); return _lp(x, 3800) * env * .12
    def strings(s, f, d, att=1.1, rel=1.5, bright=2600):
        n = int((d + rel) * SR); t = np.arange(n) / SR; x = np.zeros(n)
        for det in (-.006, -.002, .002, .006):
            for h in range(1, 12): x += np.sin(2 * np.pi * f * (1 + det) * h * t + s.rs.rand() * 6) / h
        env = np.minimum(t / att, 1) ** 1.5 * np.where(t < d, 1, np.exp(-(t - d) / (rel / 3.5))); return _lp(x, bright) * env * .16
    def musicbox(s, f, d=1.8):
        n = int(d * SR); t = np.arange(n) / SR; x = np.sin(2 * np.pi * f * t) + .4 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 6) + .2 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t * 10); return x * np.exp(-t * 2.4) * np.minimum(t / .003, 1) * .5
    def taiko(s, f=72, g=1.0):
        n = int(.9 * SR); t = np.arange(n) / SR; x = np.sin(2 * np.pi * np.cumsum(f * (.6 + .9 * np.exp(-t * 18))) / SR) * np.exp(-t * 6) + _bp(s.rs.randn(n), 900, 3500) * np.exp(-t * 60) * .35; return x * g
    def hat(s, g=1.0):
        n = int(.06 * SR); t = np.arange(n) / SR; return _hp(s.rs.randn(n), 6500) * np.exp(-t * 90) * .5 * g
    def clap(s):
        n = int(.18 * SR); t = np.arange(n) / SR; x = _bp(s.rs.randn(n), 1200, 4800) * (np.exp(-t * 28) + .6 * np.exp(-((t - .012) ** 2) * 9000)); return x * .8
    def pluck(s, f, d=.5):
        n = int(d * SR); p = max(int(SR / f), 2); b = s.rs.uniform(-1, 1, p); o = np.zeros(n)
        for i in range(n): o[i] = b[i % p]; b[i % p] = .5 * (b[i % p] + b[(i + 1) % p]) * .995
        return _lp(o, 4000) * np.exp(-np.arange(n) / SR * 3)
    def reverb(s, x, size=2.2):
        n = int(size * SR); t = np.arange(n) / SR; ir = _lp(s.rs.randn(n), 5500) * np.exp(-t * 2.6); ir[:int(.02 * SR)] *= 0; y = fftconvolve(x, ir[:n])[:len(x)]; return y / (np.abs(y).max() + 1e-6) * np.abs(x).max()
    def out(s, wetgain=.55): return s.dry + s.reverb(s.wet) * wetgain + s.reverb(s.dry, 1.2) * .12
def drive(sc, t0, t1, bpm, chords, level=lambda t: 1.0, bass=True, arps=True, hats=True, kick=True, seed=3):
    beat = 60 / bpm; bar = beat * 4; t = t0; ci = 0
    while t < t1 - .05:
        ch = chords[ci % len(chords)]; L = level(t)
        sc.put(sc.strings(midi(ch[1]), bar + .3), t, .9 * L, wet=.6); sc.put(sc.strings(midi(ch[2]), bar + .3), t, .6 * L, wet=.6)
        for b in range(16):
            tt = t + b * beat / 4
            if tt >= t1: break
            if kick and b % 8 in (0,) : sc.put(sc.sub808(midi(ch[0] - 12), 1.0), tt, 1.0 * L)
            if kick and b == 10: sc.put(sc.sub808(midi(ch[0] - 12), .6), tt, .7 * L)
            if bass and b % 4 == 2: sc.put(sc.sub808(midi(ch[0] - 12), .35, 1.2), tt, .5 * L)
            if b % 8 == 4: sc.put(sc.clap(), tt, .30 * L, wet=.3)
            if hats and b % 2 == 1: sc.put(sc.hat(.8 if b % 4 == 3 else .45), tt, .35 * L)
            if arps: sc.put(sc.pluck(midi(ch[(b * 3 + (b // 4)) % 4 + 0] + 24 if False else ch[(b) % 4] + 24), .35), tt, .22 * L * (.6 + .4 * (b % 4 == 0)), wet=.35)
        t += bar; ci += 1

# ---------------------------------------------------------------- extra instruments / styles
def ep(s, f, d=1.6):
    n = int(d * SR); t = np.arange(n) / SR; idx = 2.2 * np.exp(-t * 3.2) + .25; x = np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * f * 14 * t)) * .6 + np.sin(2 * np.pi * f * t + .8 * np.sin(2 * np.pi * f * t)) * .4
    x *= np.exp(-t * 1.8) * np.minimum(t / .004, 1) * (1 + .08 * np.sin(2 * np.pi * 4.8 * t)); return _lp(x, 3200) * .5
def cowbell(s):
    n = int(.22 * SR); t = np.arange(n) / SR; x = (np.sign(np.sin(2 * np.pi * 540 * t)) + np.sign(np.sin(2 * np.pi * 800 * t))) * .5; return _bp(x, 400, 3000) * np.exp(-t * 22) * .6
def snare(s):
    n = int(.25 * SR); t = np.arange(n) / SR; return (_bp(s.rs.randn(n), 1500, 7000) * np.exp(-t * 20) + np.sin(2 * np.pi * 190 * t) * np.exp(-t * 30) * .6) * .8
def kick(s):
    n = int(.4 * SR); t = np.arange(n) / SR; return np.sin(2 * np.pi * np.cumsum(48 + 110 * np.exp(-t * 38)) / SR) * np.exp(-t * 9) * 1.1
def vinyl(s, N):
    x = (s.rs.rand(N) > .9992) * s.rs.randn(N) * 1.6; x = _hp(x, 1500) + _lp(s.rs.randn(N), 5000) * .012; return x
def phonk(sc, t0, t1, bpm=130, level=lambda t: 1.0):
    beat = 60 / bpm; bar = beat * 4; t = t0; bi = 0; bass = [30, 30, 33, 28]; mel = [78, 81, 83, 81, 85, 83, 81, 78]
    while t < t1 - .05:
        L = level(t); root = bass[bi % 4]
        sc.put(sc.strings(midi(root + 24), bar + .3, att=.4), t, .55 * L, wet=.6)
        for b in range(16):
            tt = t + b * beat / 4
            if tt >= t1: break
            if b in (0, 7, 10): sc.put(sc.kick(), tt, .9 * L)
            if b in (0, 6, 10): sc.put(sc.sub808(midi(root), 1.1, 1.8), tt, .95 * L)
            if b == 8: sc.put(sc.snare(), tt, .55 * L, wet=.3)
            if b % 2 == 0: sc.put(sc.hat(.5 if b % 4 else .8), tt, .3 * L)
            if bi % 2 == 1 and b >= 12: sc.put(sc.hat(.6), tt, .4 * L)
            if b in (0, 3, 6, 8, 11, 14): sc.put(sc.cowbell(), tt, .22 * L)
            if b % 2 == 0: sc.put(sc.musicbox(midi(mel[(b // 2 + bi * 3) % 8]), .9), tt, .30 * L, wet=.5)
        t += bar; bi += 1
def lofi(sc, t0, t1, bpm=82, level=lambda t: 1.0):
    beat = 60 / bpm; bar = beat * 4; t = t0; ci = 0; chords = [(53, 57, 60, 64), (52, 55, 59, 62), (50, 53, 57, 60), (48, 52, 55, 59)]; mel = [72, 71, 69, 67, 64, 67, 69, 71]
    while t < t1 - .05:
        L = level(t); ch = chords[ci % 4]
        for m in ch: sc.put(sc.ep(midi(m), bar + .5), t + (.01 * ch.index(m)), .55 * L, wet=.4)
        sc.put(sc.sub808(midi(ch[0] - 24), bar * .9, 1.0), t, .55 * L)
        for b in range(16):
            tt = t + b * beat / 4 + (.018 if b % 2 else 0)
            if tt >= t1: break
            if b in (0, 10): sc.put(sc.kick(), tt, .6 * L)
            if b in (4, 12): sc.put(sc.snare(), tt, .35 * L, wet=.35)
            if b % 2 == 0: sc.put(sc.hat(.35), tt, .22 * L)
            if b in (2, 7, 11, 14) and (ci + b) % 3 != 0: sc.put(sc.ep(midi(mel[(b + ci * 2) % 8] + 12), .9), tt, .30 * L, wet=.5)
        t += bar; ci += 1
Score.ep = ep; Score.cowbell = cowbell; Score.snare = snare; Score.kick = kick; Score.vinyl = vinyl
