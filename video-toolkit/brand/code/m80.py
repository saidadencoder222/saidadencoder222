import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-saidadencoder222/21382d86-4091-5f53-a3a6-32d6a75a5607/scratchpad/c5')
import os, json, math
import numpy as np, cv2
import brand
from brand import *
SC = '/tmp/claude-0/-home-user-saidadencoder222/21382d86-4091-5f53-a3a6-32d6a75a5607/scratchpad'; WD = f'{SC}/c9/work'; FD = f'{WD}/fd81'; IM = f'{SC}/c9/img'
CUT = json.load(open(f'{WD}/cut81b.json')); WORDS = CUT['words']; DUR = CUT['dur'] + .3; NF = int(round(DUR * 30)); NFV = len(os.listdir(FD))
def eo(x): x = clamp(x); return 1 - (1 - x) ** 3
HI = {'psychologically', 'dangerous', 'niche', 'journaling', 'walk', "pavlov's", 'unhinged', 'daydreaming', 'finally'}
# ---------------------------------------------------------------- plan (windows are found from the spoken words, so everything lines up with what he says) ------
LW = [w[0].strip('.,!?').lower() for w in WORDS]
def idx(word, start=0, nth=0):
    c = 0
    for i in range(start, len(LW)):
        if LW[i] == word:
            if c == nth: return i
            c += 1
    raise KeyError(word)
T0 = lambda i: WORDS[i][1]; T1 = lambda i: WORDS[i][2] + .08
N = [i for i, w in enumerate(LW) if w == 'number']
hk_end = idx('on', idx('goes'))
TITLE = (0.0, T1(hk_end), '10 OUT OF 10 HABITS')
SUBS = [(0.0, T0(idx('but')), 'TO BECOME MORE PSYCHOLOGICALLY DANGEROUS'), (T0(idx('but')), T1(hk_end), 'BUT THEY GET MORE NICHE AS TIME GOES ON')]
s5, s4, s3, s2 = N; s1 = idx('finally') - 1
e5 = idx('day', s5); e4 = idx('planning', s4); e3 = idx('consistent', s3); e2 = idx('month', s2); e1 = len(WORDS) - 1
STACKS = [(T0(s5), T0(idx('and', idx('thoughts', s5))), 'Journaling', 'your thoughts and ideas', 'every single day'),
          (T0(s4), T0(idx('think', s4)), 'Walk', 'and think about what you should be doing', "don't waste your time"),
          (T0(s3), T0(idx('to', idx('conditioning', s3))), "Pavlov's", 'conditioning to make yourself', 'way more consistent'),
          (T0(s2), T0(idx('indulge', s2)), 'Unhinged', 'one day at the end of every month', 'so you can work hard'),
          (T0(s1), T0(idx("don't", s1)), 'Your day', 'instead of the future ahead of you', 'focus')]
IMGS = [(.3, T1(hk_end), [('hook_a', 120, 800, 235, -4), ('hook_b', 960, 770, 235, 4), ('hook_c', 940, 1070, 215, -2)]),           # three philosophy oil paintings in the hook (collage around the head, like the inspo)
        (T0(idx('and', idx('thoughts', s5))), T1(e5), [('journal', 540, 250, 640, -2)]),
        (T0(idx('think', s4)), T1(e4), [('walk', 540, 250, 640, 2)]),
        (T0(idx('to', idx('conditioning', s3))), T1(e3), [('pavlov3', 300, 255, 360, -3), ('pavlov4', 700, 235, 560, 2)]),
        (T0(idx('indulge', s2)), T0(idx('work', s2)), [('party', 540, 250, 640, -2)]),
        (T0(idx('work', s2)), T1(e2), [('fireworks', 540, 250, 640, 2)]),
        (T0(idx("don't", s1)), T1(e1), [('window1', 540, 250, 560, 2)])]
# ---------------------------------------------------------------- captions -----------------------------------------------------------------------------
def groups():
    gs, cur = [], []
    for i, w in enumerate(WORDS):
        if cur and (w[1] - cur[-1][2] > .3 or len(cur) >= 4): gs.append(cur); cur = []
        cur.append(w)
        if w[0][-1:] in '.?!,': gs.append(cur); cur = []
    if cur: gs.append(cur)
    return gs
GS = groups()
_I = {}
def load(n):
    if n not in _I: _I[n] = cv2.imread(f'{IM}/{n}.jpg')
    return _I[n]
def in_win(t, a, b): return a <= t < b
def frame(k):
    t = k / 30.0; kk = min(k, NFV - 1); raw = cv2.imread(f'{FD}/{kk + 1:04d}.jpg'); fr = brand.grade_brand(raw)
    z = 1.0
    for (a, b, *_) in [(s[0], s[1]) for s in STACKS] + [(s[0], s[1]) for s in IMGS]:
        if a <= t < b: z = 1.0 + .03 * (t - a) / max(b - a, .1); break
    f = brand.frame_speaker(fr, .9, z)
    on_img = None
    for a, b, items in IMGS:
        if a <= t < b: on_img = items; break
    if on_img:
        for (nm, cx, cy, w, rot) in on_img:
            im = load(nm)
            if im is not None: brand.paper(f, im, cx, cy, w, rot)
    if in_win(t, TITLE[0], TITLE[1]):
        sub = [x for x in SUBS if x[0] <= t < x[1]]; brand.title(f, TITLE[2], sub[0][2] if sub else SUBS[-1][2], y=255)
    st = None
    for s in STACKS:
        if s[0] <= t < s[1]: st = s; break
    if st: brand.stack(f, st[2], st[3], st[4], y=170, a=clamp((t - st[0]) / .25))
    elif True:
        for g in GS:
            a0 = g[0][1] - .02; a1 = g[-1][2] + .22
            if a0 <= t < a1:
                ws = [w[0] for w in g]; hi = {i for i, w in enumerate(ws) if w.strip('.,!?').lower() in HI}
                brand.caption(f, ws, 1330, hi=() if on_img else hi, pill=bool(on_img)); break
    return f
from simple import chunk_writer
_chunk = chunk_writer(frame)
def preview(ts, out): cv2.imwrite(out, np.hstack([cv2.resize(frame(int(t * 30)), (270, 480)) for t in ts]))
