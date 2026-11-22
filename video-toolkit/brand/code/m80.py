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
TITLE = (0.0, T1(hk_end), '10 out of 10 Habits')
SUBS = [(0.0, T0(idx('but')), 'TO BECOME MORE PSYCHOLOGICALLY DANGEROUS'), (T0(idx('but')), T1(hk_end), 'BUT THEY GET MORE NICHE AS TIME GOES ON')]
s5, s4, s3, s2 = N; s1 = idx('finally') - 1
e5 = idx('day', s5); e4 = idx('planning', s4); e3 = idx('consistent', s3); e2 = idx('month', s2); e1 = len(WORDS) - 1
STACKS = [(T0(s5), T0(idx('and', idx('thoughts', s5))), 'Journaling', 'your thoughts and ideas', 'every single day'),
          (T0(s4), T0(idx('think', s4)), 'Walk', 'and think about what you should be doing', "don't waste your time"),
          (T0(s3), T0(idx('to', idx('conditioning', s3))), "Pavlov's", 'conditioning to make yourself', 'way more consistent'),
          (T0(s2), T0(idx('indulge', s2)), 'Unhinged', 'one day at the end of every month', 'so you can work hard'),
          (T0(s1), T0(idx("don't", s1)), 'Your day', 'instead of the future ahead of you', 'focus')]
IMGS = [(.3, T1(hk_end), [('hook_a_c', 215, 240, 330, -3), ('hook_b_c', 865, 240, 330, 3)]),           # hook collage: two portraits in the headroom, one low-left (like the inspo)
        (T0(idx('and', idx('thoughts', s5))), T1(e5), [('journal', 540, 240, 800, -2)]),
        (T0(idx('think', s4)), T1(e4), [('walk', 540, 240, 800, 2)]),
        (T0(idx('to', idx('conditioning', s3))), T1(e3), [('pavlov3', 250, 235, 440, -3), ('pavlov4', 740, 235, 700, 2)]),
        (T0(idx('indulge', s2)), T0(idx('work', s2)), [('party', 540, 240, 800, -2)]),
        (T0(idx('work', s2)), T1(e2), [('fireworks', 540, 240, 800, 2)]),
        (T0(idx("don't", s1)), T1(e1), [('window1', 540, 240, 800, 2)])]
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
                u = t - a - (j * .16 if ii == 0 else 0)
                if u < 0: continue
                brand.paper(f, im, cx, cy + (0 if ii == 0 else 4 * u), w, rot, reveal=max(brand.ease(u / (.3 if ii == 0 else .2)), .02), dy=-(1 - brand.ease(u / .35)) * 140 if ii == 0 else 0)
            break
    st = None
    for s in STACKS:
        if s[0] <= t < s[1]: st = s; break
    in_title = in_win(t, TITLE[0], TITLE[1])
    if in_title:
        sub = [x for x in SUBS if x[0] <= t < x[1]]; brand.title2(f, TITLE[2], sub[0][2] if sub else SUBS[-1][2], y=1545, a=1.0)
    if st:
        si = STACKS.index(st); x_ = 400 if si % 2 == 0 else 680
        brand.accent(f, st[2], x_, 1500, t - st[0], size=170, glow=(si % 2 == 1), white_above=st[3], white_below=st[4])
    else:
        for g in GS:
            a0 = g[0][1] - .02; a1 = g[-1][2] + .22
            if a0 <= t < a1:
                ws = [FIX.get(w[0].strip('.,!?').lower(), w[0]) if 'FIX' in globals() else w[0] for w in g]; hi = {i for i, w in enumerate(ws) if w.strip('.,!?').lower() in HI}
                ci = GS.index(g); cx_, cy_ = CAPPOS[ci % len(CAPPOS)]
                if in_title: cy_ = 1320
                brand.caption_small(f, ws, cy_, hi=hi, cx=cx_, u=t - g[0][1] + .02); break
    extra(f, t)
    return f
from simple import chunk_writer
_chunk = chunk_writer(frame)
def preview(ts, out): cv2.imwrite(out, np.hstack([cv2.resize(frame(int(t * 30)), (270, 480)) for t in ts]))

# ---- motion graphics specific to the habits edit: countdown numeral + NICHE meter --------------------------------------------------------------------
HABIT_T = [T0(s5), T0(s4), T0(s3), T0(s2), T0(s1)]
def extra(f, t):
    for i, a in enumerate(HABIT_T):
        b = HABIT_T[i + 1] if i + 1 < len(HABIT_T) else 1e9
        if a <= t < b: brand.numeral(f, 5 - i, t - a)
    fr_ = 0.0
    for i, a in enumerate(HABIT_T):
        if t >= a: fr_ = (i + 1) / 5.0 if t >= a + .7 else i / 5.0 + (1 / 5.0) * brand.ease((t - a) / .7)


