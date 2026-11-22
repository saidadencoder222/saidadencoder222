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
TITLE = (0.0, T1(i_stuck), 'You\u2019re Too Smart')
SUBS = [(0.0, T1(i_stuck), 'TO GROW')]
STACKS = [(T0(i_dost), T0(idx('destroyed')), 'Dostoevsky', 'the worst sin is you have', 'destroyed yourself'),
          (T0(i_pot - 7), T0(i_pot + 1), 'Potential', 'limiting yourself behind the thing', 'you call'),
          (T0(i_ref), T0(idx('because', i_ref)), 'Your limit', 'you refuse to change your beliefs', 'because you believe you are smart'),
          (T0(i_why), T0(idx('cruised')), 'Comfortable', 'you know that you are smart', 'so you cruise'),
          (T0(i_how), T0(idx('more', i_how)), 'Combat this', 'how should you actually', 'push yourself')]
i_w = lambda w, start=0: idx(w, start)
IMGS = [(.0, T1(i_stuck), [('dostoevsky_c', 180, 1700, 340, -2), ('hook_a_c', 540, 1720, 340, 2), ('wanderer_c', 900, 1700, 340, -2)]),
        (T0(idx('dostoevsky')), T1(i_noth), [('scream', 540, 245, 820, -1)]),
        (T0(idx('but')), T1(idx('way')), [('icarus', 540, 245, 820, 1)]),
        (T0(i_pot - 6), T1(i_pot), [('hook_c_l', 540, 245, 820, -1)]),
        (T0(i_ref), T1(i_lim), [('library', 540, 245, 820, 1)]),
        (T0(idx('why')), T1(idx('comfortable')), [('window1', 540, 245, 820, -1)]),
        (T0(idx('comfortable') + 1), T1(idx('life')), [('reverie', 540, 245, 820, 1)]),
        (T0(idx('so', idx('life'))), T1(idx('uncomfortable', idx('so', idx('life')))), [('starry', 540, 245, 860, -1)]),
        (T0(idx('and', idx('uncomfortable', idx('so', idx('life'))))), T1(i_occ), [('hook_b_l', 540, 245, 820, 1)]),
        (T0(idx('more', i_how)), T1(idx('this', i_how)), [('wanderer_l', 540, 245, 820, -1)]),
        (T0(idx('this', i_how) + 1), T1(i_end), [('seneca', 540, 245, 820, 1)])]
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
ACCENTS = [   # (word index to appear on, end word index, text, x, y, white_above, white_below, glow)
    (idx('destroyed'), idx('nothing'), 'Destroyed', 370, 1440, 'the worst sin is you have', None, False),
    (idx('betrayed'), idx('nothing'), 'Betrayed', 700, 1565, 'and', None, False),
    (idx('nothing'), idx('nothing') + 1, 'nothing.', 540, 1700, 'yourself for', None, False),
    (idx('downfall'), idx('way'), 'Downfall', 540, 1500, 'a sort of', None, True),
    (idx('potential'), idx('potential') + 1, 'Potential', 540, 1500, 'the thing you call', None, True),
    (idx('limit'), idx('limit') + 1, 'Your limit', 540, 1500, 'because you believe it is', None, False),
    (idx('uncomfortable', idx('so')), idx('occur'), 'Uncomfortable', 540, 1500, 'you don\u2019t want to be', None, True)]
def ACC_draw(f, t):
    for a_, b_, txt, x, y, wa, wb, gl in ACCENTS:
        t0 = T0(a_); t1 = T1(b_) + (.25 if b_ == idx('nothing') else .0)
        if t0 <= t < t1: brand.accent(f, txt, x, y, t - t0, size=150, glow=gl, white_above=wa, white_below=wb)
def frame(k):
    t = k / 30.0; kk = min(k, NFV - 1); raw = cv2.imread(f'{FD}/{kk + 1:04d}.jpg'); fr = brand.grade_cine(raw)
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
                u = t - a
                brand.paper(f, im, cx, cy, w, rot)
            break
    st = None
    for s in STACKS:
        if s[0] <= t < s[1]: st = s; break
    in_title = in_win(t, TITLE[0], TITLE[1])
    if in_title:
        sub = [x for x in SUBS if x[0] <= t < x[1]]; brand.title2(f, TITLE[2], sub[0][2] if sub else SUBS[-1][2], y=285, a=1.0)
    acc_on = any(T0(a_) <= t < T1(b_) + (.25 if b_ == idx('nothing') else .0) for a_, b_, *_ in ACCENTS)
    if acc_on: pass
    else:
        for g in GS:
            a0 = g[0][1] - .02; a1 = g[-1][2] + .22
            if a0 <= t < a1:
                ws = [FIX.get(w[0].strip('.,!?').lower(), w[0]) if 'FIX' in globals() else w[0] for w in g]; hi = {i for i, w in enumerate(ws) if w.strip('.,!?').lower() in HI}
                ci = GS.index(g); cx_, cy_ = CAPPOS[ci % len(CAPPOS)]
                if in_title: cy_ = 1330
                brand.caption_small(f, ws, cy_, hi=hi, cx=cx_, u=t - g[0][1] + .02); break
    extra(f, t)
    return f
from simple import chunk_writer
_chunk = chunk_writer(frame)
def preview(ts, out): cv2.imwrite(out, np.hstack([cv2.resize(frame(int(t * 30)), (270, 480)) for t in ts]))

# ---- motion graphics specific to this edit: opening quote mark on the Dostoevsky line + a COMFORT -> GROWTH meter ----------------------------------------
def extra(f, t):
    pass

def extra(f, t):
    ACC_draw(f, t)
