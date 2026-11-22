import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-saidadencoder222/21382d86-4091-5f53-a3a6-32d6a75a5607/scratchpad/c5')
import os, json, math
import numpy as np, cv2
import brand
from brand import *
SC = '/tmp/claude-0/-home-user-saidadencoder222/21382d86-4091-5f53-a3a6-32d6a75a5607/scratchpad'; WD = f'{SC}/c9/work'; FD = f'{WD}/fd82'; IM = f'{SC}/c9/img'
CUT = json.load(open(f'{WD}/cut82b.json')); WORDS = CUT['words']; DUR = CUT['dur'] + .3; NF = int(round(DUR * 30)); NFV = len(os.listdir(FD))
def eo(x): x = clamp(x); return 1 - (1 - x) ** 3
HI = {'smartest', 'stuck', 'dostoevsky', 'worst', 'sin', 'potential', 'limit', 'comfortable', 'uncomfortable', 'betrayed'}
FIX = {'dostoevsky': 'Dostoevsky'}
LW = [w[0].strip('.,!?').lower() for w in WORDS]
def idx(word, start=0, nth=0):
    c = 0
    for i in range(start, len(LW)):
        if LW[i] == word:
            if c == nth: return i
            c += 1
    raise KeyError(word)
T0 = lambda i: WORDS[i][1]; T1 = lambda i: WORDS[i][2] + .08
i_stuck = idx('stuck'); i_dost = idx('dostoevsky'); i_noth = idx('nothing'); i_dont = idx("don't"); i_pot = idx('potential'); i_ref = idx('refuse') - 1; i_lim = idx('limit'); i_why = idx('why'); i_unc = idx('uncomfortable'); i_occ = idx('occur')
i_how = idx('how'); i_end = len(WORDS) - 1
TITLE = (0.0, T1(i_stuck), 'THE SMARTEST PEOPLE YOU KNOW')
SUBS = [(0.0, T1(i_stuck), 'MIGHT BE THE MOST STUCK')]
STACKS = [(T0(i_dost), T0(idx('destroyed')), 'Dostoevsky', 'the worst sin is you have', 'destroyed yourself'),
          (T0(i_pot - 7), T0(i_pot + 1), 'Potential', 'limiting yourself behind the thing', 'you call'),
          (T0(i_ref), T0(idx('because', i_ref)), 'Your limit', 'you refuse to change your beliefs', 'because you believe you are smart'),
          (T0(i_why), T0(idx('cruised')), 'Comfortable', 'you know that you are smart', 'so you cruise'),
          (T0(i_how), T0(idx('more', i_how)), 'Combat this', 'how should you actually', 'push yourself')]
IMGS = [(.3, T1(i_stuck), [('hook_a', 120, 800, 235, -4), ('wanderer_p', 960, 770, 235, 4), ('dostoevsky_p', 940, 1070, 215, -2)]),
        (T0(idx('destroyed')), T1(i_noth), [('dostoevsky_p', 540, 250, 420, -2), ('hook_b', 880, 240, 330, 3)]),
        (T0(i_dont), T1(i_pot - 7), [('wanderer_p', 540, 250, 420, 2)]),
        (T0(idx('because', i_ref)), T1(i_lim), [('hook_a', 540, 250, 420, -2)]),
        (T0(idx('cruised')), T1(i_occ), [('hook_c', 540, 250, 420, 2)]),
        (T0(idx('more', i_how)), T1(i_end), [('hook_c', 540, 250, 420, -2)])]
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
                ws = [FIX.get(w[0].strip('.,!?').lower(), w[0]) if w[0].strip('.,!?').lower() in FIX else w[0] for w in g]; hi = {i for i, w in enumerate(ws) if w.strip('.,!?').lower() in HI}
                brand.caption(f, ws, 1330, hi=() if on_img else hi, pill=bool(on_img)); break
    return f
from simple import chunk_writer
_chunk = chunk_writer(frame)
def preview(ts, out): cv2.imwrite(out, np.hstack([cv2.resize(frame(int(t * 30)), (270, 480)) for t in ts]))
