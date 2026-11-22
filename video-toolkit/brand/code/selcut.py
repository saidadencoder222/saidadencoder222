"""word-timing cut from chosen raw-time ranges. usage: selcut.py src words.json vid "a-b,c-d,..." """
import sys, json, subprocess, os, shutil
src, wj, vid, spec = sys.argv[1:5]; GAP, PA, PB, F = .21, .05, .10, .014
R = [[float(x) for x in p.split('-')] for p in spec.split(',')]
W = json.load(open(wj)); sel = [w for w in W if any(a <= (w[1] + w[2]) / 2 <= b for a, b in R)]
allw = sorted(W, key=lambda w: w[1])
def nxt(b):
    c = [w[1] for w in allw if w[1] >= b - .001 and w[2] > b + .005]
    return min([x for x in c if x > b + .005] or [b + 1])
iv = []
for k, (t, a, b) in enumerate(sel):
    prev_end = sel[k - 1][2] if k else -9; pb = min(PB, max(nxt(b) - b - .03, .02))
    if iv and a - prev_end < GAP: iv[-1][1] = b + pb
    else: iv.append([max(a - PA, 0), b + pb])
for i in range(len(iv) - 1):
    if iv[i][1] > iv[i + 1][0] - .02: m = (iv[i][1] + iv[i + 1][0]) / 2; iv[i][1] = m; iv[i + 1][0] = m
iv = [[round(a, 3), round(b, 3)] for a, b in iv]
offs = []; o = 0
for a, b in iv: offs.append(o); o += b - a
def cut(t):
    for (a, b), o_ in zip(iv, offs):
        if a - 1e-6 <= t <= b + 1e-6: return round(o_ + t - a, 3)
    return None
words = [[t, cut(a), cut(b) if cut(b) is not None else cut(a) + .2] for t, a, b in sel if cut(a) is not None]
fa = ';'.join(f'[0:v]trim={a:.3f}:{b:.3f},setpts=PTS-STARTPTS[v{i}];[0:a]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS,afade=t=in:d={F}:st=0,afade=t=out:d={F}:st={max(b - a - F, 0):.3f}[a{i}]' for i, (a, b) in enumerate(iv))
fa += ';' + ''.join(f'[v{i}][a{i}]' for i in range(len(iv))) + f'concat=n={len(iv)}:v=1:a=1[v][a]'
open(f'work/fa{vid}.txt', 'w').write(fa); json.dump(dict(iv=iv, words=words, dur=round(o, 3)), open(f'work/cut{vid}b.json', 'w'))
print('pieces', len(iv), 'dur', round(o, 2), 'words', len(words)); print(' '.join(f'{t}[{i}]' for i, (t, a, b) in enumerate(words)))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-filter_complex_script', f'work/fa{vid}.txt', '-map', '[v]', '-map', '[a]', '-r', '30', '-c:v', 'libx264', '-crf', '12', '-preset', 'fast', '-c:a', 'pcm_s16le', f'work/clip{vid}.mkv'], check=True)
shutil.rmtree(f'work/fd{vid}', ignore_errors=True); os.makedirs(f'work/fd{vid}')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'work/clip{vid}.mkv', '-qscale:v', '2', f'work/fd{vid}/%04d.jpg'], check=True); print('FRAMES', len(os.listdir(f'work/fd{vid}')))
