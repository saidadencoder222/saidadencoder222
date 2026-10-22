"""Cut dead air + flubs. usage: python3 -I cut.py N  -> work/clipN.mp4, work/clipN.segs.json, work/capN.json (words on OUT timeline)"""
import sys, json, subprocess, numpy as np, os
N = int(sys.argv[1]); R = os.path.dirname(os.path.abspath(__file__)); os.makedirs(f'{R}/work', exist_ok=True)
src = f'{R}/raw/v{N}.mp4'
W = json.load(open(f'{R}/raw/v{N}.words.json'))
if N == 3:  # medium merged two takes of 'So if you're not actually copying'; patch from small/base models (agree on timing)
    W = [w for w in W if not (20.0 <= w[1] <= 24.0)]
    for x, a0, b0 in (('So', 23.34, 23.46), ('if', 23.48, 23.55), ("you're", 23.56, 23.65), ('not', 23.66, 23.73), ('actually', 23.74, 23.96), ('copying', 23.98, 24.28)): W.append((x, a0, b0))
    W.sort(key=lambda w: w[1])
# flubs to drop: (first word start, last word start) inclusive
DROP = {1: [], 2: [(20.78, 21.89), (22.83, 26.70)], 3: [(20.05, 23.30)]}[N]

def _find(txt, after=0.0):
    for i, w in enumerate(W):
        if w[0].lower().strip('.,?!') == txt and w[1] >= after: return i
    return None
if N == 1:
    i = _find('final'); W[i] = ('funnel', W[i][1], W[i][2]); W.insert(i, ('the', W[i][1] - .12, W[i][1] - .02))
    i = _find('drive'); W[i] = ('guide', W[i][1], W[i][2]); W[i + 1] = ('on', W[i + 1][1], W[i + 1][2])
if N == 2:
    W = [w for w in W if not (22.8 <= w[1] <= 28.9)]
    for x, a0, b0 in (('each', 26.72, 26.95), ('time', 26.96, 27.12), ('he', 27.13, 27.24), ('posted', 27.25, 27.46), ('videos', 27.47, 27.78), ('he', 27.84, 27.94), ('would', 27.95, 28.05), ('have', 28.06, 28.17), ('a', 28.18, 28.30), ('team', 28.31, 28.50), ('behind', 28.51, 28.78), ('him', 28.79, 28.92)): W.append((x, a0, b0))
    W.sort(key=lambda w: w[1])
if N == 3:
    tail = [('comment', 40.56, 40.85), ('the', 40.98, 41.08), ('word', 41.12, 41.25), ('calendar', 41.30, 41.62), ('and', 41.70, 41.85), ("I'll", 41.94, 41.99), ('send', 42.00, 42.08), ('it', 42.10, 42.18), ('straight', 42.20, 42.36), ('to', 42.40, 42.52), ('you', 42.58, 42.75)]
    W = [w for w in W if w[1] < 40.5] + tail
GAP = 0.30
def dropped(a): return any(lo - .02 <= a <= hi for lo, hi in DROP)
kept = [w for w in W if not dropped(w[1]) and w[0] not in ('.', '')]
# audio energy @100Hz
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', src, '-vn', '-ac', '1', '-ar', '16000', '-f', 's16le', '-'], capture_output=True).stdout
a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768; hop = 160
rms = np.sqrt(np.convolve(a * a, np.ones(hop) / hop, 'same')[::hop] + 1e-12)
def snap(t, win=.12):
    i0 = max(int((t - win) * 100), 0); i1 = min(int((t + win) * 100) + 1, len(rms) - 1)
    return (i0 + int(np.argmin(rms[i0:i1 + 1]))) / 100
dur = len(a) / 16000
thr = max(np.percentile(rms, 8) * 3.5, 0.005)
quiet = rms < thr
cuts = []  # regions to REMOVE
st = None
for k in range(len(quiet) + 1):
    v = quiet[k] if k < len(quiet) else False
    if v and st is None: st = k
    if not v and st is not None:
        if k - st >= 20:
            a0, b0 = st / 100, k / 100
            if a0 < .01: cuts.append((0, b0 - .06))
            elif b0 > dur - .02: cuts.append((a0 + .2, dur))
            else: cuts.append((a0 + .08, b0 - .10))
        st = None
for lo, hi in DROP:
    cuts.append((snap(lo, .06), snap(hi, .06)))
cuts.sort(); merged = []
for c in cuts:
    if merged and c[0] <= merged[-1][1] + .01: merged[-1] = (merged[-1][0], max(merged[-1][1], c[1]))
    else: merged.append(c)
segs = []; p = 0.0
for lo, hi in merged:
    if lo - p > .05: segs.append((round(p, 3), round(lo, 3)))
    p = hi
if dur - p > .05: segs.append((round(p, 3), round(dur, 3)))
# out timeline
o = 0; tab = []
for s, e in segs: tab.append((s, e, o)); o += e - s
json.dump(tab, open(f'{R}/work/clip{N}.segs.json', 'w'))
def to_out(t):
    for s, e, o0 in tab:
        if s - .02 <= t <= e + .02: return o0 + max(t - s, 0)
    return None
caps = []
for w, s, e in kept:
    ts, te = to_out(s + .01), to_out(max(e - .01, s + .02))
    if ts is None: continue
    caps.append((w, round(ts, 3), round(max(te if te is not None else ts + .2, ts + .08), 3)))
json.dump({'words': caps, 'dur': o}, open(f'{R}/work/cap{N}.json', 'w'))
fv = ''; fa = ''
for k, (s, e) in enumerate(segs):
    fv += f'[0:v]trim={s}:{e},setpts=PTS-STARTPTS[v{k}];'
    fa += f'[0:a]atrim={s}:{e},asetpts=PTS-STARTPTS,afade=t=in:d=0.012,afade=t=out:st={max(e - s - .012, 0):.3f}:d=0.012[a{k}];'
cc = ''.join(f'[v{k}][a{k}]' for k in range(len(segs)))
fc = fv + fa + f'{cc}concat=n={len(segs)}:v=1:a=1[v][a]'
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-filter_complex', fc, '-map', '[v]', '-map', '[a]', '-r', '30', '-c:v', 'libx264', '-crf', '12', '-preset', 'fast', '-pix_fmt', 'yuv420p', '-c:a', 'pcm_s16le', '-ar', '48000', f'{R}/work/clip{N}.mkv'], check=True)
print(f'v{N}: {dur:.1f}s -> {o:.1f}s, {len(segs)} segments, removed {dur - o:.1f}s')
