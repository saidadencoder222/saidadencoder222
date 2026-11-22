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
TITLE = (0.0, T1(i_stuck), 'The Smartest People')
SUBS = [(0.0, T1(i_stuck), 'ARE THE MOST STUCK')]
STACKS = [(T0(i_dost), T0(idx('destroyed')), 'Dostoevsky', 'the worst sin is you have', 'destroyed yourself'),
          (T0(i_pot - 7), T0(i_pot + 1), 'Potential', 'limiting yourself behind the thing', 'you call'),
          (T0(i_ref), T0(idx('because', i_ref)), 'Your limit', 'you refuse to change your beliefs', 'because you believe you are smart'),
          (T0(i_why), T0(idx('cruised')), 'Comfortable', 'you know that you are smart', 'so you cruise'),
          (T0(i_how), T0(idx('more', i_how)), 'Combat this', 'how should you actually', 'push yourself')]
IMGS = [(.3, T1(i_stuck), [('hook_a_c', 215, 240, 330, -3), ('wanderer_c', 865, 240, 330, 3), ('dostoevsky_c', 540, 215, 250, 1)]),
        (T0(idx('destroyed')), T1(i_noth), [('dostoevsky_l', 540, 240, 800, -2)]),
        (T0(i_dont), T1(i_pot - 7), [('wanderer_l', 540, 240, 800, 2)]),
        (T0(idx('because', i_ref)), T1(i_lim), [('hook_a_l', 540, 240, 800, -2)]),
        (T0(idx('cruised')), T1(i_occ), [('hook_c_l', 540, 240, 800, 2)]),
        (T0(idx('more', i_how)), T1(i_end), [('hook_b_l', 540, 240, 800, -2)])]
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
    if n not in _I:
        im = cv2.imread(f'{IM}/{n}.jpg')
        if im is not None and not n.endswith('_c'):
            h, w = im.shape[:2]; ch = int(w * 9 / 16)
            if ch < h: y0 = int((h - ch) * .4); im = im[y0:y0 + ch]
            else: cw = int(h * 16 / 9); x0 = (w - cw) // 2; im = im[:, x0:x0 + cw]
        _I[n] = im
    return _I[n]
def in_win(t, a, b): return a <= t < b
CAPPOS = [(540, 1330), (440, 1400), (640, 1360), (500, 1450), (620, 1320), (460, 1390), (590, 1430), (540, 1350)]
CAPNOW = [0]
def frame(k):
    t = k / 30.0; kk = min(k, NFV - 1); raw = cv2.imread(f'{FD}/{kk + 1:04d}.jpg'); fr = brand.grade_brand(raw)
    z = 1.0
    for (a, b, *_) in [(s[0], s[1]) for s in STACKS] + [(s[0], s[1]) for s in IMGS]:
        if a <= t < b: z = 1.0 + .03 * (t - a) / max(b - a, .1); break
    f = brand.frame_shift(fr, 210, z)
    on_img = None
    for ii, (a, b, items) in enumerate(IMGS):
        if a <= t < b:
            on_img = items
            for j, (nm, cx, cy, w, rot) in enumerate(items):
                im = load(nm)
                if im is None: continue
                u = t - a - (j * .16 if ii == 0 else 0)
                if u < 0: continue
                brand.paper(f, im, cx, cy + (0 if ii == 0 else 4 * u), w, rot, reveal=max(brand.ease(u / (.3 if ii == 0 else .2)), .02), dy=-(1 - brand.ease(u / .35)) * 140 if ii == 0 else 0)
            break
    st = None
    for s in STACKS:
        if s[0] <= t < s[1]: st = s; break
    in_title = in_win(t, TITLE[0], TITLE[1])
    if in_title:
        sub = [x for x in SUBS if x[0] <= t < x[1]]; brand.title2(f, TITLE[2], sub[0][2] if sub else SUBS[-1][2], y=1570, a=1.0 if t > .35 else .35 + .65 * (((int(t * 30) * 7) % 3) == 0))
    if st:
        si = STACKS.index(st); x_ = 400 if si % 2 == 0 else 680
        brand.accent(f, st[2], x_, 1500, t - st[0], size=170, glow=(si % 2 == 1), white_above=st[3], white_below=st[4])
    else:
        for g in GS:
            a0 = g[0][1] - .02; a1 = g[-1][2] + .22
            if a0 <= t < a1:
                ws = [FIX.get(w[0].strip('.,!?').lower(), w[0]) if 'FIX' in globals() else w[0] for w in g]; hi = {i for i, w in enumerate(ws) if w.strip('.,!?').lower() in HI}
                ci = GS.index(g); cx_, cy_ = CAPPOS[ci % len(CAPPOS)]
                if in_title: cy_ = 1390
                brand.caption_small(f, ws, cy_, hi=hi, cx=cx_, u=t - g[0][1] + .02); break
    extra(f, t)
    return f
from simple import chunk_writer
_chunk = chunk_writer(frame)
def preview(ts, out): cv2.imwrite(out, np.hstack([cv2.resize(frame(int(t * 30)), (270, 480)) for t in ts]))

# ---- motion graphics specific to this edit: opening quote mark on the Dostoevsky line + a COMFORT -> GROWTH meter ----------------------------------------
def extra(f, t):
    pass

_extra_old = extra
def extra(f, t):
    _extra_old(f, t)
    for k, (fn) in enumerate((lambda f, u: brand.g_loop(f, 900, 1080, u), lambda f, u: brand.g_ceiling(f, 900, 1080, u, 280), lambda f, u: brand.g_ripple(f, 900, 1080, u), lambda f, u: brand.g_target(f, 900, 1080, u), lambda f, u: brand.g_check(f, 900, 1080, u))):
        t0 = STACKS[k][0]; t1 = STACKS[k + 1][0] if k + 1 < len(STACKS) else DUR
        if t0 + .15 <= t < t1: fn(f, t - t0 - .15)
