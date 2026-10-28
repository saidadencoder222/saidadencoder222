"""Prepare a raw talking-head clip for /greenscreen.
usage: python3 prep_cut.py <raw.mp4> <vid_id> <work_dir>
 1. transcribe (faster-whisper small.en, word times)   2. tighten pauses >0.3 s (energy based; never touches words)
 3. write work/cut{vid}.json (iv, words in cut time, dur) + work/fa{vid}.txt (ffmpeg concat filter)
 4. build work/clip{vid}.mkv, frames work/fd{vid}/%04d.jpg, and the RVM matte work/alpha{vid}.mkv (needs rvm.onnx, see README)
Edit the printed word list by hand for ASR errors (e.g. father's / brother's) BEFORE rendering."""
import sys, os, json, subprocess, numpy as np
from scipy.ndimage import uniform_filter1d
raw, vid, wd = sys.argv[1], sys.argv[2], sys.argv[3]; os.makedirs(wd, exist_ok=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', raw, '-vn', '-ac', '1', '-ar', '16000', f'{wd}/a.wav'], check=True)
from faster_whisper import WhisperModel
segs, _ = WhisperModel('small.en', compute_type='int8').transcribe(f'{wd}/a.wav', word_timestamps=True, language='en')
W = [[w.word.strip(), round(w.start, 2), round(w.end, 2)] for s in segs for w in s.words]
x = np.frombuffer(subprocess.check_output(['ffmpeg', '-v', 'error', '-i', raw, '-vn', '-ac', '1', '-ar', '16000', '-af', 'volume=20dB', '-f', 'f32le', '-']), np.float32)
h = 160; e = np.array([np.sqrt(np.mean(x[i:i + h] ** 2)) for i in range(0, len(x) - h, h)]); db = uniform_filter1d(20 * np.log10(e + 1e-6), 5); on = db > np.percentile(db, 10) + 8
sp = []; s = None
for i, v in enumerate(on):
    if v and s is None: s = i * .01
    if not v and s is not None: sp.append([s, i * .01]); s = None
if s is not None: sp.append([s, len(on) * .01])
m = []
for p, q in sp:
    if m and p - m[-1][1] < .30: m[-1][1] = q
    else: m.append([p, q])
iv = [[round(max(a - .06, 0), 3), round(b + .14, 3)] for a, b in m if b - a > .2]
offs = []; o = 0
for a, b in iv: offs.append(o); o += b - a
def cut(t):
    for (a, b), o_ in zip(iv, offs):
        if a - 1e-6 <= t <= b + 1e-6: return o_ + t - a
words = [[t, round(cut(a), 2), round(cut(b) if cut(b) is not None else cut(a) + .2, 2)] for t, a, b in W if cut(a) is not None]
F = .008; n = len(iv)
fa = ';'.join(f'[0:v]trim={a:.3f}:{b:.3f},setpts=PTS-STARTPTS[v{i}];[0:a]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS,afade=t=in:d={F}:st=0,afade=t=out:d={F}:st={max(b - a - F, 0):.3f}[a{i}]' for i, (a, b) in enumerate(iv))
fa += ';' + ''.join(f'[v{i}][a{i}]' for i in range(n)) + f'concat=n={n}:v=1:a=1[v][a]'
open(f'{wd}/fa{vid}.txt', 'w').write(fa); json.dump(dict(iv=iv, words=words, dur=o), open(f'{wd}/cut{vid}.json', 'w'))
print('dur', round(o, 2), 's;', len(words), 'words'); print(' '.join(f'{t}[{a}]' for t, a, b in words))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', raw, '-filter_complex_script', f'{wd}/fa{vid}.txt', '-map', '[v]', '-map', '[a]', '-r', '30', '-c:v', 'libx264', '-crf', '12', '-preset', 'fast', '-c:a', 'pcm_s16le', f'{wd}/clip{vid}.mkv'], check=True)
os.makedirs(f'{wd}/fd{vid}', exist_ok=True); subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{wd}/clip{vid}.mkv', '-qscale:v', '2', f'{wd}/fd{vid}/%04d.jpg'], check=True)
print('next: python3 rvm{0}.py (copy rvm17.py, sed clip17->clip{0}, alpha17->alpha{0}) to make the matte'.format(vid))
