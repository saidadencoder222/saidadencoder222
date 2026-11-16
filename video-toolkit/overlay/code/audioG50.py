import sys; sys.path.insert(0, '.')
import numpy as np, subprocess, importlib
from scipy.io import wavfile
from scipy.signal import butter, sosfilt
SR = 48000; DUR = 56.59 + .4; N = int(DUR * SR); rs = np.random.RandomState(21)
def bp(x, lo, hi): return sosfilt(butter(2, [lo, min(hi, SR / 2 - 100)], 'band', fs=SR, output='sos'), x)
m18 = importlib.import_module('m50')
sfx = np.zeros(N)
def click(g=1.0, f0=1100):
    n = int(.05 * SR); tt = np.arange(n) / SR; y = bp(rs.randn(n), 1800, 7000) * np.exp(-tt * 260) * .8 + np.sin(2 * np.pi * f0 * tt) * np.exp(-tt * 140) * .45
    return y / (np.abs(y).max() + 1e-9) * g
def put(x, at, g):
    i = int(at * SR)
    if i < 0 or i >= N: return
    n = min(len(x), N - i); sfx[i:i + n] += x[:n] * g
for t0, t1, kd, pp in m18.EVT[1:]:
    put(click(.8, 1000), t0 + .01, .5)                    # soft tick as each overlay lands
                                           # tiny tick on an emphasised word
put(click(1.0, 700), .0, .5)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', 'work/clip50.mkv', '-vn', '-ac', '1', '-ar', str(SR), '-af', 'highpass=f=90,afftdn=nr=14:nf=-48,agate=threshold=0.018:ratio=1.8:attack=5:release=160,acompressor=threshold=-24dB:ratio=2.4:attack=8:release=140,loudnorm=I=-14:TP=-2:LRA=7', 'work/voiceG50.wav'], check=True)
sr, v = wavfile.read('work/voiceG50.wav'); v = v.astype(np.float32) / 32768; voice = np.zeros(N, np.float32); voice[:min(N, len(v))] = v[:N]
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '12', '-t', str(DUR + 1), '-i', '../c15/Floating_Cities.mp3', '-ac', '1', '-ar', str(SR), 'work/musicG50.wav'], check=True)
sr2, mw = wavfile.read('work/musicG50.wav'); mw = mw.astype(np.float32) / 32768; mus = np.zeros(N, np.float32); mus[:min(N, len(mw))] = mw[:N]
t = np.arange(N) / SR; fade = np.minimum(np.minimum(t / 1.2, (DUR - t) / 1.8), 1) ** 2
dip = 1 - .85 * np.exp(-((t - 27.2) / .45) ** 2) * (t < 27.5) - .85 * (t >= 27.5) * np.exp(-((t - 27.2) / .9) ** 2)      # near-silence before "you feel it because he doesn't…"
env = np.convolve(np.abs(voice), np.ones(int(.15 * SR)) / int(.15 * SR), 'same'); vp = np.percentile(np.abs(voice), 99.5); duck = 1 - .5 * np.clip(env / (vp * .35), 0, 1)
rise = np.interp(t, [0, 12, 26, 38, 48, DUR], [.8, .9, 1.0, 1.2, 1.35, 1.0])
mus_d = mus * fade * dip * duck * rise
rms = lambda x: np.sqrt(np.mean(x ** 2) + 1e-12); m0 = np.abs(voice) > .02
mg = 10 ** ((-38 - 20 * np.log10(rms(mus_d[m0]) + 1e-9) + 20 * np.log10(rms(voice[m0]))) / 20)       # music about 38 dB under the voice
sg = (vp * .16) / (np.abs(sfx).max() + 1e-9); sduck = 1 - .45 * np.clip(env / (vp * .5), 0, 1)       # clicks peak at about a fifth of the voice
mix = voice + sfx * sg * sduck; mix = np.tanh(mix * 1.05) / 1.05
wavfile.write('work/mixG50_raw.wav', SR, (np.clip(mix, -1, 1) * 32767).astype(np.int16))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', 'work/mixG50_raw.wav', '-af', 'loudnorm=I=-14:TP=-2:LRA=9', 'work/mixG50.wav'], check=True); print('audio ok')
