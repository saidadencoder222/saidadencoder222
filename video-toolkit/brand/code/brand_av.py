"""/brand sound: an ORIGINAL cinematic organ-and-arpeggio bed (in the spirit of space-epic organ music, not a copy of any recording) + real SFX cues, ducked under the voice."""
import numpy as np, subprocess, wave, re, os
SR = 48000; SF = '/tmp/claude-0/-home-user-saidadencoder222/21382d86-4091-5f53-a3a6-32d6a75a5607/scratchpad/c7/sfx/'
def _load(p):
    b = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True).stdout; return np.frombuffer(b, np.float32).copy()
def _organ(freq, dur, vib=0.0, att=.03, rel=.35):
    t = np.arange(int(dur * SR)) / SR; y = np.zeros_like(t)
    for h, g in ((1, 1.0), (2, .62), (3, .42), (4, .28), (6, .16), (8, .09)):             # drawbar-style harmonics (pipe-organ-ish)
        for dt in (-1.2, 1.2): y += g * np.sin(2 * np.pi * (freq * h + dt * h * .02) * t + (vib * np.sin(2 * np.pi * 5.2 * t)))
    env = np.minimum(t / att, 1) * np.minimum((dur - t) / rel + .0, 1).clip(0, 1); return (y * env).astype(np.float32)
def _reverb(x, sec=2.6, wet=.28):
    n = int(sec * SR); ir = np.random.RandomState(3).randn(n).astype(np.float32) * np.exp(-np.arange(n) / (sec * SR / 5.5)); ir /= np.abs(ir).sum() * .02 + 1e-6
    from scipy.signal import fftconvolve
    return x * (1 - wet) + fftconvolve(x, ir)[:len(x)] * wet
def music(dur, bpm=96):
    """slow pedal chords in D minor/Bb/F/C feel, over a repeating rising arpeggio (original pattern)"""
    N = int(dur * SR); out = np.zeros(N + 4 * SR, np.float32); beat = 60 / bpm
    chords = [(146.83, [293.66, 349.23, 440.0, 587.33]), (116.54, [233.08, 293.66, 349.23, 466.16]), (174.61, [261.63, 349.23, 440.0, 523.25]), (130.81, [261.63, 329.63, 392.0, 523.25])]
    bar = 4 * beat; nb = int(dur / bar) + 2
    for b in range(nb):
        root, tones = chords[b % 4]; s = int(b * bar * SR)
        pad = _organ(root, bar + .6, .5, .12, .6) * .55 + _organ(root * 2, bar + .6, .3, .15, .6) * .3
        for f_ in tones[:3]: pad += _organ(f_, bar + .6, .4, .2, .6) * .16
        if s < len(out): out[s:s + len(pad)] += pad[:len(out) - s]
        pat = [0, 1, 2, 3, 2, 1, 2, 3]                                                  # arpeggio, 8th notes
        for k in range(8):
            f_ = tones[pat[k]] * (2 if k % 4 == 3 else 1); a = _organ(f_, .5, .25, .006, .24) * .21; s2 = int((b * bar + k * beat / 2) * SR)
            if s2 < len(out): out[s2:s2 + len(a)] += a[:len(out) - s2]
    out = _reverb(out[:N], 2.6, .3); out /= np.abs(out).max() + 1e-6; return out
def _peak_idx(x): return int(np.argmax(np.convolve(np.abs(x), np.ones(240) / 240, 'same')))
def mix(voice_wav, cues, dur, out_wav, music_db=-23, music_path=None):
    """cues = [(sfx_name, time_of_peak_s, peak_dBFS, max_len_s_or_None)]; music ducks under the voice"""
    v = _load(voice_wav); N = int(dur * SR); voice = np.zeros(N, np.float32); voice[:min(len(v), N)] = v[:N]
    m = _load(music_path) if music_path else music(dur); m = np.pad(m, (0, max(N - len(m), 0)))[:N]
    env = np.convolve(np.abs(voice), np.ones(int(.06 * SR)) / (.06 * SR), 'same'); env = np.convolve(env, np.ones(int(.25 * SR)) / (.25 * SR), 'same'); env = np.clip(env / (np.percentile(env, 95) + 1e-6), 0, 1)
    duck = 1 - .55 * env; fade = np.minimum(np.arange(N) / (1.5 * SR), 1) * np.minimum((N - np.arange(N)) / (2.2 * SR), 1)
    mus = m * duck * fade; mus *= 10 ** (music_db / 20) / (np.sqrt(np.mean(mus ** 2)) + 1e-6) * 10 ** (-14 / 20 + .0) if False else 1
    # music level: RMS -> target loudness about -27 LUFS-ish under a -14 LUFS voice
    r = np.sqrt(np.mean((m * duck * fade) ** 2)) + 1e-6; mus = (m * duck * fade) * (10 ** (music_db / 20) / r) * .1
    mix = voice + mus; sf = {}
    for name, t, db, ml in cues:
        if name not in sf: sf[name] = _load(f'{SF}{name}.wav')
        x = sf[name].copy()
        if ml: x = x[:int(ml * SR)]
        pk = _peak_idx(x); x = x / max(np.abs(x).max(), 1e-6) * 10 ** (db / 20); f = int(.004 * SR); x[:f] *= np.linspace(0, 1, f); x[-f * 6:] *= np.linspace(1, 0, f * 6)
        s = int(t * SR) - pk; a, b = max(s, 0), min(s + len(x), N)
        if b > a: mix[a:b] += x[a - s:b - s]
    pk = np.abs(mix).max(); mix = mix / pk * .93 if pk > .93 else mix
    a16 = (np.clip(mix, -1, 1) * 32767).astype(np.int16); w = wave.open(out_wav, 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(a16.tobytes()); w.close()
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', out_wav, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True)
    return re.findall(r'I:\s+(-?[\d.]+) LUFS', r.stderr)[-1], re.findall(r'Peak:\s+(-?[\d.]+) dBFS', r.stderr)[-1]
if __name__ == '__main__':
    m = music(20); print(m.shape, np.abs(m).max())
    a16 = (m * .5 * 32767).astype(np.int16); w = wave.open('/tmp/claude-0/-home-user-saidadencoder222/21382d86-4091-5f53-a3a6-32d6a75a5607/scratchpad/c9/work/music_test.wav', 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(a16.tobytes()); w.close()
