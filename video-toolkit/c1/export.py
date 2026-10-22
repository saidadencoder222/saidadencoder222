import os, sys, json, subprocess, numpy as np, cv2, multiprocessing as mp
from cc import *
import vids
OUT = f'{R}/out/capcut'; os.makedirs(OUT, exist_ok=True)
def srt_t(t): ms = int(round(t * 1000)); return f'{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}'
def anim_job(a):
    N, k = a; scenes, G = vids.setup(N); s = scenes[k]; d = s.t1 - s.t0 - (.5 if k == len(scenes) - 1 else 0)
    out = f'{OUT}/video{N}/anim_{k:02d}_{int(s.t0 * 10):03d}s.mp4'
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', '30', '-i', '-', '-c:v', 'libx264', '-crf', '16', '-preset', 'fast', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for n in range(int(d * 30)):
        t = s.t0 + n / 30; enc.stdin.write(np.ascontiguousarray(filmgrain(scene_frame(s, t, None), n, .03)).tobytes())
    enc.stdin.close(); enc.wait(); return out
if __name__ == '__main__':
    jobs = []
    for N in (1, 2, 3):
        os.makedirs(f'{OUT}/video{N}', exist_ok=True); scenes, G = vids.setup(N)
        jobs += [(N, k) for k, s in enumerate(scenes) if s.kind == 'anim']
        d = json.load(open(f'{R}/work/cap{N}.json'))['dur']
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{R}/work/clip{N}g.mkv', '-i', f'{R}/work/voice{N}.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-crf', '18', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-shortest', f'{OUT}/video{N}/00_speaker_cut_graded.mp4'], check=True)
        subprocess.run(['cp', f'{R}/work/voice{N}.wav', f'{OUT}/video{N}/voice_clean.wav'])
        with open(f'{OUT}/video{N}/captions.srt', 'w') as f:
            for i, g in enumerate(G, 1): f.write(f"{i}\n{srt_t(g['t0'])} --> {srt_t(g['t1'])}\n{g['txt'].lower()}\n\n")
        with open(f'{OUT}/video{N}/timeline.txt', 'w') as f:
            f.write(f'VIDEO {N}  total {d:.1f}s\nTrack 1 = 00_speaker_cut_graded.mp4 (full length, carries the voice). Put each animation clip on Track 2 at the start time below, covering the speaker. Animations have no audio.\n\n')
            for k, s in enumerate(scenes):
                if s.kind == 'anim': f.write(f'  {s.t0:6.1f}s -> {min(s.t1, d):6.1f}s   anim_{k:02d}_{int(s.t0 * 10):03d}s.mp4   ({s.title[0]} / {s.title[1]})\n')
                else: f.write(f'  {s.t0:6.1f}s -> {min(s.t1, d):6.1f}s   speaker visible (zoom {s.z[0]:.2f}->{s.z[1]:.2f}, punch-in on cuts)\n')
    with mp.Pool(4) as p: p.map(anim_job, jobs, chunksize=1)
    print('done', len(jobs), 'anim clips')
