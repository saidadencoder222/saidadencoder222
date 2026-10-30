import sys, json, subprocess, numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt
SR = 48000; d = json.load(open('work/cut30.json')); DUR = d['dur']; N = int(DUR * SR); rs = np.random.RandomState(7)
bp = lambda x, lo, hi: sosfilt(butter(2, [lo, hi], 'band', fs=SR, output='sos'), x)
def click(f0=1100):
    n = int(.05 * SR); tt = np.arange(n) / SR; y = bp(rs.randn(n), 1800, 7000) * np.exp(-tt * 260) * .8 + np.sin(2 * np.pi * f0 * tt) * np.exp(-tt * 140) * .45; return y / np.abs(y).max()
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', 'work/clip30.mkv', '-vn', '-ac', '1', '-ar', str(SR), '-af', 'highpass=f=90,afftdn=nr=12:nf=-48,agate=threshold=0.018:ratio=1.8:attack=5:release=160,acompressor=threshold=-24dB:ratio=2.4:attack=8:release=140,loudnorm=I=-14:TP=-2:LRA=7', 'work/t30/voice.wav'], check=True)
sr, v = wavfile.read('work/t30/voice.wav'); v = v.astype(np.float32) / 32768; voice = np.zeros(N, np.float32); voice[:min(N, len(v))] = v[:N]
CLK = [0.2, 6.15, 11.3, 20.25, 28.1, 33.4]
sfx = np.zeros(N)
for t in CLK:
    c = click(1000); i = int(t * SR); sfx[i:i + len(c)] += c * .5; c2 = click(1400); i2 = i + int(.28 * SR); sfx[i2:i2 + len(c2)] += c2 * .28
vp = np.percentile(np.abs(voice), 99.5); sg = vp * .2 / np.abs(sfx).max(); mix = voice + sfx * sg; mix = np.tanh(mix * 1.05) / 1.05
wavfile.write('work/t30/mix_raw.wav', SR, (np.clip(mix, -1, 1) * 32767).astype(np.int16))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', 'work/t30/mix_raw.wav', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=9,alimiter=limit=0.89', 'work/t30/mix.wav'], check=True)
sr, m = wavfile.read('work/t30/mix.wav'); m = np.abs(m.astype(np.float32) / 32768); K = 240; pk = [float(m[int(i * len(m) / K):int((i + 1) * len(m) / K)].max()) for i in range(K)]
json.dump(dict(dur=DUR, peaks=pk, clicks=CLK), open('work/t30/wave.json', 'w'))
# raw-time words for the transcript tile
iv = d['iv']; offs = []; o = 0
for a, b in iv: offs.append(o); o += b - a
def raw(t):
    for (a, b), o_ in zip(iv, offs):
        if o_ - 1e-6 <= t <= o_ + (b - a) + 1e-6: return a + t - o_
json.dump([[w, round(raw(a), 2)] for w, a, b in d['words'] if raw(a) is not None], open('work/t30/words_raw.json', 'w'))
print('audio ok')
