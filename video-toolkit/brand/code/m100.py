import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-saidadencoder222/21382d86-4091-5f53-a3a6-32d6a75a5607/scratchpad/c5')
import os, json, math
import numpy as np, cv2
import brand
from brand import *
SC = '/tmp/claude-0/-home-user-saidadencoder222/21382d86-4091-5f53-a3a6-32d6a75a5607/scratchpad'; WD = f'{SC}/c13/work'; FD = f'{WD}/fd100'; IM = f'{SC}/c13/img'
CUT = json.load(open(f'{WD}/cut100b.json')); WORDS = CUT['words']; IV = CUT['iv']; DUR = CUT['dur'] + .3; NF = int(round(DUR * 30)); NFV = len(os.listdir(FD))
OFF = []; o = 0
for a, b in IV: OFF.append(o); o += b - a
def cutt(t):
    for (a, b), o_ in zip(IV, OFF):
        if t <= b + .001: return o_ + max(t - a, 0)
    return OFF[-1] + IV[-1][1] - IV[-1][0]
HI = {'vip', 'broke,', 'broke', 'no.', 'genuine.', 'genuine', 'result', '$3,000', 'grab', 'opportunity,', 'free', 'money'}
LW = [w[0].lower() for w in WORDS]
def idx(word, start=0):
    for i in range(start, len(LW)):
        if LW[i].strip('.,!?') == word: return i
    raise KeyError(word)
T0 = lambda i: WORDS[i][1]; T1 = lambda i: WORDS[i][2] + .08
B = lambda t: cutt(t)                                                  # raw seconds -> edited seconds (beat times from the approved storyboard)
TITLE = (0.0, B(6.7), 'The Lowest Budget Business')
SUBS = [(0.0, B(6.7), 'YOU CAN POSSIBLY START')]
IMGS = [(.0, B(6.7), [('m0', 185, 150, 340, -1), ('reg', 540, 135, 340, 1), ('pair', 895, 150, 340, -1)]),
        (B(8.2), B(15.3), [('phone', 540, 330, 840, -1)]),
        (B(17.6), B(20.5), [('m1', 540, 330, 840, 1)]),
        (B(20.5), B(24.3), [('contract', 540, 330, 840, -1)]),
        (B(29.5), B(36.6), [('handshake', 540, 330, 840, 1)]),
        (B(44.5), B(51.5), [('reg', 540, 330, 840, -1)]),
        (B(57.9), B(65.0), [('contract', 540, 330, 840, 1)]),
        (B(65.8), B(79.6), [('handshake', 540, 330, 840, -1)])]
ACCENTS = [(idx('vip'), idx('vip') + 1, 'VIP', 'the only thing between her and being in a', True),
           (idx('broke'), idx('broke') + 1, 'Broke', 'we all been there, we all been', True),
           (idx('no', idx('said')), idx('no', idx('said')) + 1, 'No.', 'she said', False),
           (idx('genuine'), idx('genuine') + 1, 'Genuine', 'how you can help them and be', True),
           (idx('result'), idx('result') + 1, 'The result', 'people that do have the', True),
           (idx('$3,000'), idx('$3,000') + 1, '$3,000', 'a minimum of', True),
           (idx('grab'), idx('grab') + 1, 'Grab it', 'if you’ve been handed opportunity, just go', True)]
def ix(word, start=0, default=None):
    try: return idx(word, start)
    except KeyError: return default
_say = ix('said'); _no = ix('no', _say) if _say is not None else None
GFX = [(ix('story'), ix('story') + 1, 'write'), (ix('phone'), ix('phone') + 7, 'ripple'), (ix('there'), ix('underpaid'), 'burst'), (ix('offered'), _no, 'target'), (ix('genuine'), ix('genuine') + 3, 'check'),
       (ix('literally'), ix('literally') + 6, 'path'), (ix('free'), ix('product'), 'ceiling'), (ix('minimum'), ix('person'), 'burst'), (ix('promise'), len(WORDS) - 1, 'loop')]
GFX = [g for g in GFX if None not in g]
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
CAPPOS = [(540, 1790), (470, 1830), (610, 1800), (510, 1850), (590, 1780), (480, 1820), (570, 1840), (540, 1800)]
def ACC_active(t): return any(T0(a_) <= t < T1(b_) + .3 for a_, b_, *_ in ACCENTS)
def footage(k, z):
    raw = cv2.imread(f'{FD}/{min(k, NFV - 1) + 1:04d}.jpg')[:835]                                  # her burned-in title is below y 835: cropped off. Colour untouched.
    im = cv2.resize(raw, (1080, 1252), interpolation=cv2.INTER_CUBIC)
    can = np.zeros((1920, 1080, 3), np.uint8); can[668:] = im
    row = cv2.GaussianBlur(im[:24].mean(0, keepdims=True), (0, 0), 45); ext = np.repeat(row, 668, 0)
    ext = (ext * (.62 + .38 * np.linspace(0, 1, 668, dtype=np.float32)[:, None, None])).astype(np.uint8)              # the wall colour continued upward, a little darker toward the top
    can[:668] = ext; g = np.linspace(0, 1, 40, dtype=np.float32)[:, None, None]; can[628:668] = (ext[-40:].astype(np.float32) * (1 - g) + im[:40].astype(np.float32) * g).astype(np.uint8)
    if z != 1.0: can = cv2.warpAffine(can, np.float32([[z, 0, 540 - z * 540], [0, z, 1300 - z * 1300]]), (1080, 1920), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return can
def frame(k):
    t = k / 30.0; z = 1.0
    for (a, b, *_) in IMGS:
        if a <= t < b: z = 1.0 + .03 * (t - a) / max(b - a, .1); break
    f = footage(k, z)
    for a, b, items in IMGS:
        if a <= t < b:
            for (nm, cx, cy, w, rot) in items:
                im = load(nm)
                if im is not None: brand.paper(f, im, cx, cy, w, rot)
            break
    if TITLE[0] <= t < TITLE[1]: brand.title2(f, TITLE[2], SUBS[0][2], y=540, a=1.0)
    for a_, b_, txt, wa, gl in ACCENTS:
        if T0(a_) <= t < T1(b_) + .3: brand.accent(f, txt, 540, 1800, t - T0(a_), size=130, glow=gl, white_above=wa)
    for a_, b_, kind in GFX:
        t0, t1 = T0(a_), T1(b_)
        if t0 <= t < t1 + .2 and not (TITLE[0] <= t < TITLE[1]):
            u = t - t0
            {'write': lambda: brand.g_write(f, 760, 980, u), 'ripple': lambda: brand.g_ripple(f, 900, 1000, u), 'burst': lambda: brand.g_burst(f, 900, 1000, u), 'target': lambda: brand.g_target(f, 900, 1000, u), 'check': lambda: brand.g_check(f, 900, 1000, u), 'path': lambda: brand.g_path(f, 740, 1000, u), 'ceiling': lambda: brand.g_ceiling(f, 760, 860, u, 280), 'loop': lambda: brand.g_loop(f, 900, 1020, u)}[kind]()
    if not ACC_active(t):
        for g in GS:
            a0 = g[0][1] - .02; a1 = g[-1][2] + .22
            if a0 <= t < a1:
                ws = [w[0] for w in g]; hi = {i for i, w in enumerate(ws) if w.lower() in HI}; ci = GS.index(g); cx_, cy_ = CAPPOS[ci % len(CAPPOS)]
                brand.caption_small(f, ws, cy_, hi=hi, cx=cx_, u=t - g[0][1] + .02); break
    return f
from simple import chunk_writer
_chunk = chunk_writer(frame)
def preview(ts, out): cv2.imwrite(out, np.hstack([cv2.resize(frame(int(t * 30)), (270, 480)) for t in ts]))
