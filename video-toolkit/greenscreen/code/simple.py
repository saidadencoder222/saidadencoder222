"""Minimal state + caption layer for the /greenscreen engine (re-created: the original was lost with the old scratchpad)."""
import sys, os, json, math
C2 = '/tmp/claude-0/-home-user-saidadencoder222/21382d86-4091-5f53-a3a6-32d6a75a5607/scratchpad/c2'; C5 = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, C2)
import numpy as np, cv2
import doc
from doc import *
WHITE = (255, 255, 255)
class _S3:
    STATE = {}
    def setup(self, vid, color=WHITE, extra=()):
        d = json.load(open(f'{C5}/work/cut{vid}.json')); words = [(t, a, b) for t, a, b in d['words']]
        VDUR = d['dur']; DUR = VDUR + .4
        self.STATE.clear(); self.STATE.update(vid=vid, VDUR=VDUR, DUR=DUR, NF=int(round(DUR * FPS)), words=words, color=color)
S3 = _S3()
_CG = {}
def cap_groups(words):
    gs, cur = [], []
    for w in words:
        if cur and (w[1] - cur[-1][2] > .35 or len(cur) >= 4): gs.append(cur); cur = []
        cur.append(w)
        if w[0][-1:] in '.?!,': gs.append(cur); cur = []
    if cur: gs.append(cur)
    return gs
def captions(f, t, words, y=1600, size=58):
    """ONE simple caption stream: Inter 600, lowercase, white, soft shadow, 1-4 word chunks."""
    key = id(words)
    if key not in _CG: _CG[key] = cap_groups(words)
    for g in _CG[key]:
        a0 = g[0][1] - .03; a1 = g[-1][2] + .2
        if a0 <= t < a1:
            s = ' '.join(w[0] for w in g).lower().replace(' .', '.'); sz = size
            while twidth(s, 'inter', sz, 0, 600) > 940 and sz > 24: sz -= 2
            m = tex(s, 'inter', sz, 0, 600); a = clamp((t - a0) / .08) * clamp((a1 - t) / .1)
            put(f, m, 540, y, (0, 0, 0), a * .55, blur=9, dy=5); put(f, m, 540, y, WHITE, a); return
def chunk_writer(frame):
    import subprocess
    def _chunk(args):
        a, b, path = args
        p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-crf', '12', '-preset', 'fast', '-pix_fmt', 'yuv420p', path], stdin=subprocess.PIPE)
        for k in range(a, b): p.stdin.write(frame(k).tobytes())
        p.stdin.close(); p.wait(); return path
    return _chunk
def speaker(*a, **k): raise NotImplementedError
def cine(*a, **k): raise NotImplementedError
