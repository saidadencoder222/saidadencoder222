"""usage: python3 mkcut.py <src.mp4> <words.json> <vid> "a-b,c-d,..."   (raw-time keep intervals, in story order)
builds work/clip<vid>.mkv (1080x1920, 30fps), frames work/fd<vid>/%04d.jpg, work/cut<vid>.json (words in cut time, dur)"""
import sys, os, json, subprocess, shutil
src, wj, vid, spec = sys.argv[1:5]; wd = 'work'; F = .018
iv = [[float(x) for x in p.split('-')] for p in spec.split(',')]
W = json.load(open(wj)); offs = []; o = 0
for a, b in iv: offs.append(o); o += b - a
words = []
for t, a, b in W:
    mid = (a + b) / 2
    for (x, y), o_ in zip(iv, offs):
        if x <= mid <= y: words.append([t, round(o_ + max(a, x) - x, 2), round(o_ + min(b, y) - x, 2)]); break
n = len(iv)
fa = ';'.join(f'[0:v]trim={a:.3f}:{b:.3f},setpts=PTS-STARTPTS[v{i}];[0:a]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS,afade=t=in:d={F}:st=0,afade=t=out:d={F}:st={max(b - a - F, 0):.3f}[a{i}]' for i, (a, b) in enumerate(iv))
fa += ';' + ''.join(f'[v{i}][a{i}]' for i in range(n)) + f'concat=n={n}:v=1:a=1[v][a]'
open(f'{wd}/fa{vid}.txt', 'w').write(fa); json.dump(dict(iv=iv, words=words, dur=round(o, 3)), open(f'{wd}/cut{vid}.json', 'w'))
print('dur', round(o, 2), 'words', len(words)); print(' '.join(f'{t}[{i}]' for i, (t, a, b) in enumerate(words)))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-filter_complex_script', f'{wd}/fa{vid}.txt', '-map', '[v]', '-map', '[a]', '-r', '30', '-vf', 'scale=1080:1920', '-c:v', 'libx264', '-crf', '12', '-preset', 'fast', '-c:a', 'pcm_s16le', f'{wd}/clip{vid}.mkv'], check=True) if False else None
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-filter_complex_script', f'{wd}/fa{vid}.txt', '-map', '[v]', '-map', '[a]', '-r', '30', '-c:v', 'libx264', '-crf', '12', '-preset', 'fast', '-c:a', 'pcm_s16le', f'{wd}/clip{vid}.mkv'], check=True)
shutil.rmtree(f'{wd}/fd{vid}', ignore_errors=True); os.makedirs(f'{wd}/fd{vid}')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{wd}/clip{vid}.mkv', '-qscale:v', '2', f'{wd}/fd{vid}/%04d.jpg'], check=True)
print('FRAMES', len(os.listdir(f'{wd}/fd{vid}')))
