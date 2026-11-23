import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-saidadencoder222/21382d86-4091-5f53-a3a6-32d6a75a5607/scratchpad/c5')
import os, json, math
import numpy as np, cv2
import brand
from brand import *
SC = '/tmp/claude-0/-home-user-saidadencoder222/21382d86-4091-5f53-a3a6-32d6a75a5607/scratchpad'; WD = f'{SC}/c12/work'; FD = f'{WD}/fd90'; IM = f'{SC}/c12/img'
CUT = json.load(open(f'{WD}/cut90b.json')); WORDS = CUT['words']; DUR = CUT['dur'] + .3; NF = int(round(DUR * 30)); NFV = len(os.listdir(FD))
HI = {'problem', 'buyer', 'pitch', 'fail', 'trusted', 'meaningful', 'understand', 'ask', 'line', 'sales', 'closes'}
LW = [w[0].strip('.,!?').lower() for w in WORDS]
def idx(word, start=0):
    for i in range(start, len(LW)):
        if LW[i] == word: return i
    raise KeyError(word)
T0 = lambda i: WORDS[i][1]; T1 = lambda i: WORDS[i][2] + .08
i_enough = idx('enough'); i_buyer = idx('buyer'); i_pitch = idx('pitch'); i_fail = idx('fail'); i_call = idx('call', i_fail); i_trust = idx('trusted'); i_mean = idx('meaningful'); i_proc = idx('process'); i_save = idx('save'); i_ask = idx('ask'); i_line = idx('line')
TITLE = (0.0, T1(i_enough), '10 Years In Sales')
SUBS = [(0.0, T0(idx('they')), 'ONE THING I UNDERSTOOD ABOUT CLOSES'), (T0(idx('they')), T1(i_enough), 'THEY DON’T GO INTO THE PROBLEM WELL ENOUGH')]
IMGS = [(.0, T1(i_enough), [('m0', 185, 330, 360, -1), ('reg', 540, 310, 360, 1), ('pair', 895, 330, 360, -1)]),
        (T0(idx('if')), T1(i_buyer), [('handshake', 540, 500, 880, -1)]),
        (T0(idx('and', i_buyer)), T1(i_pitch), [('phone', 540, 500, 880, 1)]),
        (T0(idx('exactly')), T1(idx('you', idx('buy'))), [('contract', 540, 500, 880, -1)]),
        (T0(idx('this', idx('buy'))), T1(i_call), [('m1', 540, 500, 880, 1)]),
        (T0(i_save), T1(len(WORDS) - 1), [('phone', 540, 500, 880, -1)])]
ACCENTS = [(idx('problem'), idx('enough'), 'Problem', 540, 1790, 'they don’t go into the', 'well enough', True),
           (i_buyer, i_buyer + 1, 'Buyer', 540, 1790, 'if you don’t understand your', None, False),
           (i_pitch, i_pitch + 1, 'The pitch', 540, 1790, 'minutes into', None, True),
           (i_fail, i_fail + 1, 'Fail', 540, 1790, 'inevitably make you', None, True),
           (i_trust, i_trust + 1, 'Trusted', 540, 1790, 'they’re not going to feel', None, False),
           (i_mean, i_mean + 1, 'Meaningful', 540, 1790, 'a', 'problem', True),
           (i_ask, i_ask + 1, 'Ask', 540, 1790, 'what could I potentially', 'them', True)]
def groups():
    gs, cur = [], []
    for w in WORDS:
        if cur and (w[1] - cur[-1][2] > .3 or len(cur) >= 4): gs.append(cur); cur = []
        cur.append(w)
        if w[0][-1:] in '.?!,': gs.append(cur); cur = []
    if cur: gs.append(cur)
    return gs
GS = groups(); _I = {}
def load(n):
    if n not in _I:
        im = cv2.imread(f'{IM}/{n}.jpg')
        if im is not None:
            h, w = im.shape[:2]; ch = int(w * 9 / 16)
            if ch < h: y0 = int((h - ch) * .4); im = im[y0:y0 + ch]
            else: cw = int(h * 16 / 9); x0 = (w - cw) // 2; im = im[:, x0:x0 + cw]
        _I[n] = im
    return _I[n]
CAPPOS = [(540, 1790), (460, 1830), (620, 1800), (500, 1850), (600, 1780), (470, 1820), (580, 1840), (540, 1800)]
def ACC_active(t): return any(T0(a_) <= t < T1(b_) for a_, b_, *_ in ACCENTS)
def footage(k, z):
    raw = cv2.imread(f'{FD}/{min(k, NFV - 1) + 1:04d}.jpg')[:880]                                  # the creator's burned-in captions start below y 880: cropped off
    im = brand.grade_cine(cv2.resize(raw, (1080, 1320), interpolation=cv2.INTER_CUBIC))
    can = np.zeros((1920, 1080, 3), np.uint8); can[600:] = im
    ext = cv2.GaussianBlur(im[:600][::-1].copy(), (0, 0), 3); can[:600] = ext                       # headroom: the ceiling continued (mirrored)
    g = np.linspace(0, 1, 40, dtype=np.float32)[:, None, None]; can[560:600] = (ext[-40:].astype(np.float32) * (1 - g) + im[:40].astype(np.float32) * g).astype(np.uint8)
    if z != 1.0: can = cv2.warpAffine(can, np.float32([[z, 0, 540 - z * 540], [0, z, 1300 - z * 1300]]), (1080, 1920), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return can
def frame(k):
    t = k / 30.0; z = 1.0
    for (a, b, *_) in IMGS:
        if a <= t < b: z = 1.0 + .03 * (t - a) / max(b - a, .1); break
    f = footage(k, z); on_img = None
    for ii, (a, b, items) in enumerate(IMGS):
        if a <= t < b:
            on_img = items
            for (nm, cx, cy, w, rot) in items:
                im = load(nm)
                if im is not None: brand.paper(f, im, cx, cy, w, rot)
            break
    if TITLE[0] <= t < TITLE[1]:
        sub = [x for x in SUBS if x[0] <= t < x[1]]; brand.title2(f, TITLE[2], sub[0][2] if sub else SUBS[-1][2], y=700, a=1.0)
    for a_, b_, txt, x, y, wa, wb, gl in ACCENTS:
        if T0(a_) <= t < T1(b_): brand.accent(f, txt, x, y, t - T0(a_), size=150, glow=gl, white_above=wa, white_below=wb)
    if not ACC_active(t):
        for g in GS:
            a0 = g[0][1] - .02; a1 = g[-1][2] + .22
            if a0 <= t < a1:
                ws = [w[0] for w in g]; hi = {i for i, w in enumerate(ws) if w.strip('.,!?').lower() in HI}; ci = GS.index(g); cx_, cy_ = CAPPOS[ci % len(CAPPOS)]
                if TITLE[0] <= t < TITLE[1]: cy_ = 1790
                brand.caption_small(f, ws, cy_, hi=hi, cx=cx_, u=t - g[0][1] + .02); break
    return f
from simple import chunk_writer
_chunk = chunk_writer(frame)
def preview(ts, out): cv2.imwrite(out, np.hstack([cv2.resize(frame(int(t * 30)), (270, 480)) for t in ts]))
