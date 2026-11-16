import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-saidadencoder222/21382d86-4091-5f53-a3a6-32d6a75a5607/scratchpad/c5')
import os, math, json
import numpy as np, cv2
from simple import *
import grade51 as G
import bscenes as B                      # WB look helper (imports the engine; only look() is used)
doc.FILES.update({'serifb': 'CrimsonPro-Bold.ttf', 'inter': 'Inter.ttf'})
S3.setup(51, WHITE); S = S3.STATE; B.set_wall([118, 160, 200])
SC = '/tmp/claude-0/-home-user-saidadencoder222/21382d86-4091-5f53-a3a6-32d6a75a5607/scratchpad/c6'; GOT = f'{SC}/got'; BF = f'{SC}/work/bfr'
VDUR = S['VDUR']; DUR = VDUR + .4; NF = int(round(DUR * FPS)); WH = (255, 255, 255); YEL = (185, 248, 248); LBLUE = (235, 202, 174)         # BGR (the reference's pale yellow + light blue)
# --- ASR fixes (flagged to the user) ---
W_ = [list(w) for w in S['words']]
def fixw(i, txt): W_[i][0] = txt
fixw(69, 'is House'); fixw(70, 'Stark.'); fixw(125, 'pays his'); fixw(126, 'debts.')
S['words'] = [tuple(w) for w in W_]
T = lambda i: S['words'][i][1]                                                             # start time of word i
# --- overlay plan: (first_word, end_word, kind, params).  Each overlay ends when the next begins. ---
EV = [
 (0, 10, 'pop', ('Game of Thrones is such a', 'masterclass', 'in branding')),
 (10, 19, 'clip', [(6.13, 7.23), (2.6, 3.07), (10.23, 10.9)]),
 (19, 32, 'clip', [(0.0, 1.03), (8.27, 9.27), (3.6, 4.1)]),
 (32, 35, 'clip', [(4.07, 5.07), (5.07, 5.4)]),
 (35, 41, 'list', ['1. Symbols', '2. Mottos', '3. Color scheme']),
 (41, 52, 'clip', [(14.47, 16.6), (13.27, 14.47)]),
 (52, 62, 'trio', None),
 (62, 66, 'sigil', 'stark'),
 (66, 70, 'img', 'wf4'),
 (70, 76, 'img', 'dragon1'),
 (76, 82, 'sigil', 'targ'),
 (82, 87, 'sigil', 'lann'),
 (87, 93, 'trio', None),
 (93, 102, 'pop', ('Your content needs', 'visual identity', 'of its own')),
 (102, 107, 'pop', ('Second thing is', 'the motto', '')),
 (107, 119, 'quad', None),
 (119, 126, 'motto', 'lann'),
 (126, 131, 'motto', 'stark'),
 (131, 144, 'pop', ('You need something that can', 'visually distinguish', 'yourself from the rest')),
 (144, 150, 'palette', None),
 (150, 159, 'img', 'wf1'),
 (159, 167, 'img', 'dorne2'),
 (167, 182, 'img2', ['kl2', 'kl6']),
 (182, 190, 'pop', ('You need to have a', 'specific color scheme', '')),
 (190, 207, 'clip', [(17.6, 19.6), (16.6, 17.13), (7.23, 8.27)]),
]
sh = lambda i: i if i <= 66 else i + 1
EV = [(sh(a), sh(b), k, p) for a, b, k, p in EV]
EVT = [(T(a), (T(b) if b < len(S['words']) else VDUR + .4), k, p) for a, b, k, p in EV]
# --- card builders (each returns a BGR image with the white edge, plus alpha) ---
EDGE = 6; CW, CH = 700, 394; BOTTOM = 512
_I = {}
def load(name):
    if name not in _I:
        p = f'{GOT}/{name}.png'; im = cv2.imread(p, cv2.IMREAD_UNCHANGED) if os.path.exists(p) else cv2.imread(f'{GOT}/{name}.jpg')
        _I[name] = im
    return _I[name]
def cover(im, w, h, fx=.5, fy=.5):
    if im.ndim == 3 and im.shape[2] == 4: im = im[..., :3]
    ih, iw = im.shape[:2]; s = max(w / iw, h / ih); r = cv2.resize(im, (int(math.ceil(iw * s)), int(math.ceil(ih * s))), interpolation=cv2.INTER_AREA if s < 1 else cv2.INTER_CUBIC)
    x0 = int((r.shape[1] - w) * fx); y0 = int((r.shape[0] - h) * fy); return r[y0:y0 + h, x0:x0 + w]
def framed(inner):
    h, w = inner.shape[:2]; out = np.full((h + 2 * EDGE, w + 2 * EDGE, 3), 255, np.uint8); out[EDGE:EDGE + h, EDGE:EDGE + w] = inner; return out
def shield(name, w, h, bg=(238, 236, 232)):
    im = load(name); canvas = np.full((h, w, 3), bg, np.uint8)
    if im is None: return canvas
    s = min(w * .8 / im.shape[1], h * .84 / im.shape[0]); r = cv2.resize(im, (int(im.shape[1] * s), int(im.shape[0] * s)), interpolation=cv2.INTER_AREA)
    a = r[..., 3:4].astype(np.float32) / 255 if r.shape[2] == 4 else np.ones(r.shape[:2] + (1,), np.float32); x0 = (w - r.shape[1]) // 2; y0 = (h - r.shape[0]) // 2
    canvas[y0:y0 + r.shape[0], x0:x0 + r.shape[1]] = (canvas[y0:y0 + r.shape[0], x0:x0 + r.shape[1]] * (1 - a) + r[..., :3] * a).astype(np.uint8); return canvas
def txt_img(w, h, bg, lines, name, sizes, cols, ys, track=0):
    c = np.full((h, w, 3), bg, np.uint8)
    for ln, sz, col, y in zip(lines, sizes, cols, ys):
        sz = fit(ln, name, sz, w - 60, track) if False else sz
        while twidth(ln, name, sz, track) > w - 50 and sz > 20: sz -= 2
        put(c, tex(ln, name, sz, track), w / 2, y, (0, 0, 0), .0); put(c, tex(ln, name, sz, track), w / 2, y, col, 1.0)
    return c
_CARD = {}
def card_static(kind, p):
    key = (kind, str(p))
    if key in _CARD: return _CARD[key]
    if kind == 'img': inner = cover(load(p), CW, CH)
    elif kind == 'sigil': inner = shield({'stark': 'sig_stark', 'targ': 'sig_targ', 'lann': 'sig_lann'}[p], 380, 410)
    elif kind == 'trio':
        inner = np.full((330, 720, 3), (238, 236, 232), np.uint8)
        for i, n in enumerate(('sig_stark', 'sig_targ', 'sig_lann')): inner[:, i * 240:(i + 1) * 240] = shield(n, 240, 330)
    elif kind == 'quad':
        inner = np.full((300, 760, 3), (238, 236, 232), np.uint8)
        for i, n in enumerate(('sig_stark', 'sig_targ', 'sig_lann', 'sig_martell')): inner[:, i * 190:(i + 1) * 190] = shield(n, 190, 300)
    elif kind == 'motto':
        bgc, sig, l1, l2 = {'lann': ((38, 24, 140), 'sig_lann', 'A Lannister always', 'pays his debts'), 'stark': ((84, 82, 78), 'sig_stark', 'Winter', 'is coming')}[p]
        inner = np.full((300, 700, 3), bgc, np.uint8); sh = shield(sig, 230, 280, bgc); inner[10:290, 20:250] = sh[:280, :230]
        for ln, y in ((l1, 118), (l2, 188)):
            sz = 78
            while twidth(ln, 'serifb', sz) > 400 and sz > 30: sz -= 2
            put(inner, tex(ln, 'serifb', sz), 480, y, (255, 255, 255), 1.0)
    elif kind == 'palette':
        inner = np.full((300, 700, 3), (238, 236, 232), np.uint8)
        for i, (col, lab) in enumerate((((153, 122, 92), 'Winterfell: cold, dark'), ((59, 163, 224), 'Dorne: bright, warm'), ((46, 38, 179), "King's Landing: red"))):
            x0 = 20 + i * 223; inner[20:220, x0:x0 + 205] = col
            sz = 22
            while twidth(lab, 'inter', sz, 0, 600) > 200 and sz > 14: sz -= 1
            put(inner, tex(lab, 'inter', sz, 0, 600), x0 + 102, 255, (40, 40, 44), 1.0)
    elif kind == 'list':
        inner = np.full((330, 560, 3), 255, np.uint8)
        for i, ln in enumerate(p): put(inner, tex(ln, 'inter', 44, 0, 700), 40 + twidth(ln, 'inter', 44, 0, 700) / 2, 60 + i * 100, LBLUE, 1.0)
    out = framed(inner); _CARD[key] = out; return out
def clip_frame(segs, u):
    t = u
    for a, b in segs:
        if t < b - a: return cv2.imread(f'{BF}/{min(int((a + t) * 30) + 1, 659):04d}.jpg')
        t -= (b - a)
    a, b = segs[-1]; return cv2.imread(f'{BF}/{min(int((b - .04) * 30) + 1, 659):04d}.jpg')
def card_image(kind, p, u):
    if kind == 'clip': return framed(cover(clip_frame(p, u), CW, CH))
    if kind == 'img2': return card_static('img', p[0] if u < (u_len_cache.get(str(p), 1.9)) else p[1])
    return card_static(kind, p)
u_len_cache = {}
def paste_card(f, card, u):
    h, w = card.shape[:2]; e = clamp(u / .16); sc = .93 + .07 * eo(e); a = clamp(u / .08)
    if sc != 1: card = cv2.resize(card, None, fx=sc, fy=sc, interpolation=cv2.INTER_LINEAR); h, w = card.shape[:2]
    cx = 540; y1 = int(BOTTOM - (1 - sc) * 0); y0 = y1 - h; x0 = cx - w // 2
    sh = np.zeros((h + 60, w + 60), np.float32); sh[30:30 + h, 30:30 + w] = 1; sh = cv2.GaussianBlur(sh, (0, 0), 14) * .32 * a
    sy0 = y0 + 6 - 30; sx0 = x0 - 30; ys0, ys1 = max(sy0, 0), min(sy0 + sh.shape[0], H); xs0, xs1 = max(sx0, 0), min(sx0 + sh.shape[1], W)
    reg = f[ys0:ys1, xs0:xs1].astype(np.float32); m = sh[ys0 - sy0:ys1 - sy0, xs0 - sx0:xs1 - sx0, None]; f[ys0:ys1, xs0:xs1] = (reg * (1 - m)).astype(np.uint8)
    reg = f[y0:y0 + h, x0:x0 + w]
    if reg.shape[:2] == card.shape[:2]: f[y0:y0 + h, x0:x0 + w] = (reg.astype(np.float32) * (1 - a) + card.astype(np.float32) * a).astype(np.uint8)
def text_pop(f, lines, u):
    e = clamp(u / .16); sc = .93 + .07 * eo(e); a = clamp(u / .1); l1, big, l2 = lines
    ys = [168, 290, 410] if l2 else [190, 315, 0]
    for ln, y, kind in ((l1, ys[0], 'w'), (big, ys[1], 'y'), (l2, ys[2], 'w')):
        if not ln: continue
        if kind == 'w':
            sz = 58
            while twidth(ln, 'inter', sz, 0, 600) > 900 and sz > 30: sz -= 2
            m = tex(ln, 'inter', sz, 0, 600); col = WH
        else:
            sz = 150
            while twidth(ln, 'serifb', sz) > 920 and sz > 40: sz -= 4
            m = tex(ln, 'serifb', sz); col = YEL
        put(f, m, 540, y, (0, 0, 0), a * .38, blur=12, dy=6, sc=sc); put(f, m, 540, y, col, a, sc=sc)
_CG = {}
def cap_groups(words):
    gs, cur = [], []
    for w in words:
        if cur and (w[1] - cur[-1][2] > .35 or len(cur) >= 4): gs.append(cur); cur = []
        cur.append(w)
        if w[0][-1:] in '.?!,': gs.append(cur); cur = []
    if cur: gs.append(cur)
    return gs
def caps(f, t, words, y=1345, size=46):
    """the reference's caption: small white sans, original sentence case, soft shadow"""
    key = id(words)
    if key not in _CG: _CG[key] = cap_groups(words)
    for g in _CG[key]:
        a0 = g[0][1] - .03; a1 = g[-1][2] + .2
        if a0 <= t < a1:
            s = ' '.join(w[0] for w in g); sz = size
            while twidth(s, 'inter', sz, 0, 600) > 860 and sz > 30: sz -= 2
            m = tex(s, 'inter', sz, 0, 600); a = clamp((t - a0) / .06) * clamp((a1 - t) / .08)
            put(f, m, 540, y, (0, 0, 0), a * .5, blur=7, dy=3); put(f, m, 540, y, WH, a); return
EMPH = [6, 8, 38, 58, 65, 75, 81, 86, 101, 106, 125, 130, 149, 153, 162, 170, 189]       # words that get a close-up punch
def zoom(t):
    """camera motion on the footage: ping-pong zoom-ins/outs across each overlay (1.03 to 1.10) plus a quick close-up punch on emphasised words. Overlay cards stay fixed."""
    z = 1.04
    for i, (t0, t1, kd, pp) in enumerate(EVT):
        if t0 - .03 <= t < t1:
            u = clamp((t - t0) / max(t1 - t0, .1)); a, b = (1.03, 1.10) if i % 2 == 0 else (1.10, 1.03); z = a + (b - a) * eio(u); break
    for i in EMPH:
        d = t - T(sh(i))
        if 0 <= d < .55: z += .05 * (eo(d / .12) if d < .12 else 1 - eio((d - .12) / .43))
    return z
def pan(t, z):
    """slow horizontal/vertical drift, direction alternating per overlay; kept inside the crop margin so no edges show"""
    px = py = 0.0
    for i, (t0, t1, kd, pp) in enumerate(EVT):
        if t0 - .03 <= t < t1:
            u = clamp((t - t0) / max(t1 - t0, .1)); d = 1 if i % 2 == 0 else -1; px = d * (u * 2 - 1) * .8; py = (-1 if i % 3 == 0 else 1) * (u * 2 - 1) * .5; break
    mx = (z - 1) * 540 * .9; my = (z - 1) * 960 * .45
    return px * mx, py * my
def footage(k):
    raw = cv2.imread(f"{SC.replace('c6', 'c5')}/work/fd51/{min(k, NFV - 1) + 1:04d}.jpg"); raw = cv2.resize(raw[10:], (1080, 1920), interpolation=cv2.INTER_LINEAR); fr = G.warm_grade(raw); t_ = k / FPS; z = zoom(t_); px, py = pan(t_, z)
    if True: fr = cv2.warpAffine(fr, np.float32([[z, 0, 540 - z * 540 + px], [0, z, 820 - z * 820 + py]]), (1080, 1920), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return fr       # crop the thin bright band at the top edge
NFV = int(VDUR * 30)
def frame(k):
    t = k / FPS; f = footage(k)
    for t0, t1, kind, p in EVT:
        if t0 - .03 <= t < t1:
            u = max(t - t0, 0.0)
            if kind == 'pop': text_pop(f, p, u)
            elif kind == 'img2':
                half = (t1 - t0) / 2; paste_card(f, card_static('img', p[0] if u < half else p[1]), u if u < half else u - half)
            else: paste_card(f, card_image(kind, p, u), u)
            break
    caps(f, t, S['words'], 1470, 46)
    return f
_chunk = chunk_writer(frame)
def preview(ts, out): cv2.imwrite(out, np.hstack([cv2.resize(frame(int(t * FPS)), (270, 480)) for t in ts]))
