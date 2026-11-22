import json, subprocess, os, shutil
d = json.load(open('work/cut80b.json')); W = d['words']; dur = d['dur']; KEEP = .13
iv = []; cur = 0.0
for i in range(len(W) - 1):
    g = W[i + 1][1] - W[i][2]
    if g > KEEP + .06:
        iv.append([cur, round(W[i][2] + KEEP / 2, 3)]); cur = round(W[i + 1][1] - KEEP / 2, 3)
iv.append([cur, dur]); F = .012
offs = []; o = 0
for a, b in iv: offs.append(o); o += b - a
def cut(t):
    for (a, b), o_ in zip(iv, offs):
        if a - 1e-6 <= t <= b + 1e-6: return round(o_ + t - a, 3)
    return None
W2 = [[t, cut(a) if cut(a) is not None else cut(min(b, a + .05)), cut(b) if cut(b) is not None else None] for t, a, b in W]
for w in W2:
    if w[2] is None: w[2] = w[1] + .2
fa = ';'.join(f'[0:v]trim={a:.3f}:{b:.3f},setpts=PTS-STARTPTS[v{i}];[0:a]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS,afade=t=in:d={F}:st=0,afade=t=out:d={F}:st={max(b - a - F, 0):.3f}[a{i}]' for i, (a, b) in enumerate(iv))
fa += ';' + ''.join(f'[v{i}][a{i}]' for i in range(len(iv))) + f'concat=n={len(iv)}:v=1:a=1[v][a]'
open('work/fa81.txt', 'w').write(fa); json.dump(dict(iv=iv, words=W2, dur=round(o, 3)), open('work/cut81b.json', 'w'))
print('pieces', len(iv), 'dur', round(o, 2), 'was', dur)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', 'work/clip80.mkv', '-filter_complex_script', 'work/fa81.txt', '-map', '[v]', '-map', '[a]', '-r', '30', '-c:v', 'libx264', '-crf', '12', '-preset', 'fast', '-c:a', 'pcm_s16le', 'work/clip81.mkv'], check=True)
shutil.rmtree('work/fd81', ignore_errors=True); os.makedirs('work/fd81')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', 'work/clip81.mkv', '-qscale:v', '2', 'work/fd81/%04d.jpg'], check=True)
print('FRAMES', len(os.listdir('work/fd81')))
