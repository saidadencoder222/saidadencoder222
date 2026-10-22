"""Sound design: original synthesized score + SFX (licence-free) mixed under the voice with ducking."""
import numpy as np, subprocess, json, os
from scipy.signal import butter, sosfilt, fftconvolve, lfilter
from scipy.io import wavfile
R = os.path.dirname(os.path.abspath(__file__)); SR = 48000; T = 29.0; N = int(T * SR); rs = np.random.RandomState(3)
t_ = np.arange(N) / SR
def noise(n=None): return rs.randn(N if n is None else n)
def bp(x, lo, hi, o=2): return sosfilt(butter(o, [lo / (SR / 2), min(hi, SR / 2 - 100) / (SR / 2)], 'band', output='sos'), x)
def lp(x, fc, o=2): return sosfilt(butter(o, fc / (SR / 2), 'low', output='sos'), x)
def hp(x, fc, o=2): return sosfilt(butter(o, fc / (SR / 2), 'high', output='sos'), x)
def env_pts(pts):  # [(t, gain)] piecewise-smooth
    ts, gs = zip(*pts); g = np.interp(t_, ts, gs); return lp(g, 6, 1)
def place(buf, sig, t0, g=1.0):
    i = int(t0 * SR)
    if i < 0 or i >= len(buf): return
    n = min(len(sig), len(buf) - i); buf[i:i + n] += sig[:n] * g
def adsr_noise(dur, lo, hi, att=.02, dec=8):
    n = int(dur * SR); x = bp(noise(n), lo, hi); e = np.minimum(np.arange(n) / (att * SR + 1), 1) * np.exp(-np.arange(n) / SR * dec); return x * e
def boom(dur=1.8, f0=52, f1=28):
    n = int(dur * SR); t = np.arange(n) / SR; ph = 2 * np.pi * np.cumsum(f1 + (f0 - f1) * np.exp(-t * 5)) / SR
    return np.sin(ph) * np.exp(-t * 2.6) * 1.0 + lp(noise(n), 300) * np.exp(-t * 14) * .5
def thud(g=1.0, f=60): n = int(.35 * SR); t = np.arange(n) / SR; return np.sin(2 * np.pi * np.cumsum(f * .55 + f * .45 * np.exp(-t * 22)) / SR) * np.exp(-t * 11) * g
def whoosh(dur=.5, up=True):
    n = int(dur * SR); x = noise(n); y = np.zeros(n); k = 6
    for i in range(k):
        a, b = int(n * i / k), int(n * (i + 1) / k); fc = 400 + (3800 if up else -3000) * (i / k) if up else 3400 - 2800 * (i / k); y[a:b] = bp(x[a:b], max(fc * .6, 200), fc * 1.5)
    e = np.sin(np.pi * np.linspace(0, 1, n)) ** 1.6; return y * e
def riser(dur, g=1.0):
    n = int(dur * SR); t = np.arange(n) / SR; u = t / dur; f = 110 * (9 ** u); ph = 2 * np.pi * np.cumsum(f) / SR
    return (np.sin(ph) * .35 + bp(noise(n), 500, 7000) * .55 * u ** 1.6) * (u ** 1.8) * g
def click(g=1.0, f=2600): n = int(.012 * SR); return bp(noise(n), f, f * 2.2) * np.exp(-np.arange(n) / SR * 380) * g
def shutter(g=1.0): s = np.zeros(int(.2 * SR)); place(s, click(1.4, 1800), 0); place(s, click(1.0, 1300), .075); place(s, adsr_noise(.1, 600, 2400, .001, 40), 0, .25); return s * g
def paper(dur=.4, g=1.0): return adsr_noise(dur, 900, 5500, .06, 7) * g
def heartbeat(buf, t0, t1, bpm=62, g=.5):
    per = 60 / bpm; t = t0
    while t < t1: place(buf, thud(g, 58), t); place(buf, thud(g * .6, 52), t + .21); t += per
def drone(g):
    out = np.zeros(N)
    for f, a in ((55, 1.0), (82.41, .55), (110, .35), (164.8, .15)):
        for dt in (-.4, 0, .4): out += a * np.sin(2 * np.pi * (f + dt) * t_ + rs.rand() * 6.28 + 2.2 * np.sin(2 * np.pi * .07 * t_)) * .33
    out = lp(out, 420) + .25 * lp(bp(noise(), 90, 400), 400) * (.6 + .4 * np.sin(2 * np.pi * .11 * t_)); return out * g
def pad(chords, g):
    out = np.zeros(N)
    for (t0, t1, notes) in chords:
        env = np.clip(np.minimum((t_ - t0) / 2.0, (t1 - t_) / 2.0), 0, 1) ** 1.3
        s = np.zeros(N)
        for f in notes:
            for dt in (-.7, .0, .6): s += np.sin(2 * np.pi * (f + dt) * t_ + rs.rand() * 6.28) + .4 * np.sin(2 * np.pi * 2 * (f + dt) * t_ + rs.rand() * 6.28)
        out += lp(s, 1100) * env * .06
    return out * g
def reverb(x, wet=.3, dur=2.2):
    n = int(dur * SR); ir = noise(n) * np.exp(-np.arange(n) / SR * 2.2); ir = lp(ir, 5000); ir /= np.sqrt(np.sum(ir ** 2)); return x * (1 - wet) + fftconvolve(x, ir)[:len(x)] * wet * 1.4

from scipy.ndimage import maximum_filter1d
def glitch_blip(g=1.0):
    """one short, understated digital glitch: sample-held, bit-crushed noise stutter + tiny pitch blip"""
    n = int(.15 * SR); x = bp(noise(n), 900, 7000); x = np.repeat(x[::14], 14)[:n]; x = np.round(x * 3) / 3
    gate = ((np.arange(n) // int(.011 * SR)) % 3 != 1).astype(float); t = np.arange(n) / SR
    blip = np.sin(2 * np.pi * np.cumsum(2200 * np.exp(-t * 14) + 500) / SR) * np.exp(-t * 30) * .6
    return (x * gate * np.exp(-t * 16) * .8 + blip) * g
def fade_io(x, a=.4, b=1.2):
    e = np.ones(len(x)); i = int(a * SR); j = int(b * SR); e[:i] = np.linspace(0, 1, i) ** 2; e[-j:] = np.linspace(1, 0, j) ** 2; return x * e
# ---------------- build (v2: quieter, cleaner)
music = drone(1.0) * env_pts([(0, 0), (.8, .25), (1.8, .55), (3.4, .42), (6.2, .50), (7.2, .70), (7.5, .04), (8.15, .04), (8.45, .40), (13.5, .40), (14.65, .70), (15.9, .45), (19.6, .32), (22.0, .55), (24.9, .75), (26.4, .22), (27.6, .40), (29, 0)])
music += pad([(0, 8.2, (110, 130.8, 164.8)), (8.0, 13.8, (110, 130.8, 164.8, 220)), (13.5, 22.2, (87.3, 110, 130.8, 174.6)), (21.8, 26.6, (73.4, 110, 146.8, 174.6)), (26.2, 29.3, (110, 130.8, 164.8))], 1.0) * env_pts([(0, .0), (2, .7), (6.9, .9), (7.5, .08), (8.45, .8), (24.9, 1.1), (26.4, .35), (29, 0)])
heartbeat(music, 19.7, 26.3, 62, .28); heartbeat(music, 26.9, 28.2, 50, .2)
music = hp(reverb(music, .22), 70)                                                                      # no sub rumble under the voice
sfx = np.zeros(N)
def P(sig, t0, g): place(sfx, np.concatenate([np.linspace(0, 1, int(.003 * SR)), np.ones(max(len(sig) - int(.003 * SR), 0))])[:len(sig)] * sig, t0, g)
P(riser(1.65), .2, .30); P(boom(2.2), 1.85, .50); P(click(1.5, 3000), 1.85, .22)                           # '536'
P(lp(noise(int(2.6 * SR)), 140) * np.sin(np.pi * np.linspace(0, 1, int(2.6 * SR))) ** .8, 3.9, .45)         # soft rumble under the eruption
P(riser(1.15), 6.3, .26); P(thud(1.0, 70), 6.88, .35); P(boom(2.0, 46, 26), 7.45, .55)                      # 18 months -> blackout (silence follows)
P(glitch_blip(1.0), 8.68, .30)                                                                          # the ONE glitch sound (title reveal)
for tt in (10.9, 14.9, 23.4): P(click(1.0, 3500), tt, .22)
P(boom(2.0, 56, 30), 14.68, .45); P(paper(.45), 14.7, .30)                                              # 1315
P(paper(.5, 1.0), 15.72, .38); P(thud(1.2, 52), 16.08, .42); P(thud(1.3, 48), 17.45, .45)                # famine
rain = hp(noise(int(1.5 * SR)), 1800) * .5 + bp(noise(int(1.5 * SR)), 500, 1800) * .25; rain *= np.sin(np.pi * np.linspace(0, 1, len(rain))) ** .9; P(rain, 18.45, .22)
P(shutter(.9), 22.15, .45); P(shutter(.9), 23.25, .40); P(shutter(.9), 24.05, .40); P(paper(.5), 24.33, .35)  # archive photos
P(boom(2.4, 60, 30), 25.0, .55); P(adsr_noise(.35, 100, 3000, .001, 9), 25.0, .30)                      # CRASHED
P(boom(2.6, 44, 24), 27.65, .30)                                                                        # end card
sfx = reverb(sfx, .18, 1.6)
# ---------------- voice
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{R}/work/clip.mkv', '-vn', '-ac', '1', '-af', 'highpass=f=80,afftdn=nr=14:nf=-42,equalizer=f=250:t=q:w=1:g=-2,equalizer=f=3000:t=q:w=1.1:g=3,equalizer=f=7500:t=q:w=1.5:g=-3,acompressor=threshold=-22dB:ratio=3:attack=6:release=120:makeup=4,loudnorm=I=-16:TP=-2:LRA=7', '-ar', str(SR), f'{R}/work/voice.wav'], check=True)
sr, v = wavfile.read(f'{R}/work/voice.wav'); v = v.astype(np.float64) / 32768; voice = np.zeros(N); voice[:min(len(v), N)] = v[:N]
env = np.abs(voice); env = lp(env, 8, 1); env = np.clip(env / (np.percentile(env, 95) + 1e-6), 0, 1)
env = maximum_filter1d(env, int(.30 * SR)); env = lp(env, 2.5, 1)                                         # quick duck on speech, slower recovery in pauses
duck = 1 - .56 * np.clip(env, 0, 1)
MUSIC_G, SFX_G = float(os.environ.get('MG', '.16')), .15
music_d = fade_io(music * duck * MUSIC_G, .5, 1.3); sfx_m = fade_io(sfx * SFX_G, .05, .9)
np.savez(f'{R}/work/stems2.npz', voice=voice, music=music_d, sfx=sfx_m)
mix = voice + music_d + sfx_m
wavfile.write(f'{R}/work/mix_raw.wav', SR, (np.clip(mix, -1, 1) * 32767).astype(np.int16))
r = subprocess.run(['ffmpeg', '-v', 'info', '-i', f'{R}/work/mix_raw.wav', '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True).stderr
I = float([l for l in r.splitlines() if 'I:' in l and 'LUFS' in l][-1].split('I:')[1].split('LUFS')[0]); g = -14.0 - I; print('pre-gain loudness', I, '-> gain', round(g, 2), 'dB')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{R}/work/mix_raw.wav', '-af', f'volume={g}dB,alimiter=limit=0.84:level=disabled', '-ar', '48000', '-ac', '2', f'{R}/work/mix.wav'], check=True)
G = 10 ** (g / 20); print('applied gain', round(g, 2))
def db(x): return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9)
sp = env > .35; pz = (env < .10) & (np.arange(len(env)) > int(1.0 * SR)) & (np.arange(len(env)) < int(27.0 * SR))
print('FINAL levels (dBFS RMS):  voice (speaking) %.1f | music while speaking %.1f | music in pauses %.1f | sfx peak %.1f dBFS' % (db(voice[sp] * G), db(music_d[sp] * G), db(music_d[pz] * G) if pz.sum() else -99, 20 * np.log10(np.abs(sfx_m * G).max())))
