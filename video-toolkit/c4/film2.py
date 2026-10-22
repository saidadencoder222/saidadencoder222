import sys, os, json, math, subprocess
S = '/tmp/vt'
sys.path.insert(0, f'{S}/c2')
import numpy as np, cv2
import doc
from doc import W, H, FPS, clamp, sm, eo, eio, lerp, back, tex, twidth, put, text, over, kb, prep_alpha, spk, warp
doc.FILES.update({'pb': 'Poppins-Bold.ttf', 'psb': 'Poppins-SemiBold.ttf', 'pm': 'Poppins-Medium.ttf'})
C4 = f'{S}/c4'; CUT = json.load(open(f'{C4}/work/cut.json')); WORDS = CUT['words']; VDUR = CUT['dur']; DUR = VDUR + .9; NF = int(round(DUR * FPS))
OFFW = (226, 234, 238); CHAR = (22, 20, 20); GREY = (150, 150, 150)
AMBER = (40, 170, 255); TEAL = (190, 190, 40); STEEL = (225, 160, 95)
_IC = {}
def getimg(k):
    if k not in _IC:
        a = cv2.imread(img(k)); h, w = a.shape[:2]
        if w > 2600: a = cv2.resize(a, (2600, int(h * 2600 / w)), interpolation=cv2.INTER_AREA)
        _IC[k] = a
    return _IC[k]

doc.FILES.update({'bebas': 'BebasNeue.ttf'})
FD = f'{C4}/films'
FILES_ = dict(int_poster='int_poster.jpg', int_end='int_endurance.jpg', int_bh='int_bh.png', tdk_poster='tdk_poster.jpg', tdk_tumbler='tdk_tumbler.jpg', pir_poster='pirates_poster.png', int_ice='int_glacier.jpg')
_IC = {}
def getimg(k):
    if k not in _IC:
        a = cv2.imread(f'{FD}/{FILES_[k]}')
        if a.shape[1] > 1900: a = cv2.resize(a, (1900, int(a.shape[0] * 1900 / a.shape[1])), interpolation=cv2.INTER_AREA)
        _IC[k] = a
    return _IC[k]
def cardimg(k, w, sweep=-1.0):
    im = getimg(k); h = int(im.shape[0] * w / im.shape[1]); big = cv2.resize(im, (w, h), interpolation=cv2.INTER_CUBIC)
    bl = cv2.GaussianBlur(big, (0, 0), 1.4); big = cv2.addWeighted(big, 1.6, bl, -.6, 0)
    big = np.clip(big.astype(np.float32) + np.random.RandomState(3).randn(h, w, 1).astype(np.float32) * 4, 0, 255).astype(np.uint8)
    if 0 <= sweep <= 1:
        xx = np.arange(w, dtype=np.float32)[None, :] + np.arange(h, dtype=np.float32)[:, None] * .45; c = lerp(-80, w + h * .45 + 80, sweep); band = np.clip(1 - np.abs(xx - c) / 70, 0, 1) ** 2 * .55
        big = np.clip(big.astype(np.float32) + band[..., None] * 255, 0, 255).astype(np.uint8)
    cv2.rectangle(big, (0, 0), (w - 1, h - 1), (235, 235, 235), 2); return big
def paste(f, im, cx, cy, a=1.0, shadow=.6):
    h, w = im.shape[:2]; x0, y0 = int(cx - w / 2), int(cy - h / 2); X0, Y0, X1, Y1 = max(x0, 0), max(y0, 0), min(x0 + w, W), min(y0 + h, H)
    if X0 >= X1 or Y0 >= Y1 or a <= .01: return
    if shadow > 0:
        sh = np.zeros((H, W), np.float32); sh[Y0:Y1, X0:X1] = 1; sh = np.roll(cv2.GaussianBlur(sh, (0, 0), 24), 22, 0); f[:] = (f.astype(np.float32) * (1 - shadow * a * sh[..., None])).astype(np.uint8)
    roi = f[Y0:Y1, X0:X1].astype(np.float32); src = im[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0].astype(np.float32); f[Y0:Y1, X0:X1] = (roi * (1 - a) + src * a).astype(np.uint8)
def bgimg(k, t, u, blur, dim, tint, z0=1.0, z1=1.2, cx=.5):
    im = getimg(k); a = kb(im, u * 5, 5, z0, z1, (cx, .5), (cx, .5), interp=cv2.INTER_LINEAR)
    if blur: a = cv2.GaussianBlur(a, (0, 0), blur)
    a = a.astype(np.float32) * dim; return np.clip(a * .85 + np.array(tint, np.float32) * dim * .2, 0, 255).astype(np.uint8)
# ---- burn text
_N = {}
def noise(sh, seed):
    k = (sh, seed)
    if k not in _N:
        r = np.random.RandomState(seed); n = cv2.GaussianBlur(r.rand(*sh).astype(np.float32), (0, 0), 5) * .6 + cv2.GaussianBlur(r.rand(*sh).astype(np.float32), (0, 0), 1.6) * .4
        n = (n - n.min()) / (n.max() - n.min()); _N[k] = n
    return _N[k]
def burn(f, s, name, size, x, y, p, t, accent=AMBER, track=0, color=OFFW, a=1.0):
    if p <= 0: return
    m = tex(s, name, size, track); n = noise(m.shape, abs(hash(s)) % 9999); thr = p * 1.3 - .15
    rev = np.clip((thr - n) / .09, 0, 1) * m; edge = np.clip(1 - np.abs(n - thr) / .07, 0, 1) * m
    put(f, rev, x, y, color, a); put(f, edge * .9, x, y, accent, a * (1 - .8 * clamp((p - 1) / .5)), blur=2.5, add=True)
    if p < 1.4:
        ys, xs = np.where((np.abs(n - thr) < .02) & (m > .4))
        if len(ys):
            r = np.random.RandomState(int(t * 30)); idx = r.choice(len(ys), min(10, len(ys)), replace=False); h, w = m.shape
            for i in idx:
                px = int(x - w / 2 + xs[i] + r.randn() * 6); py = int(y - h / 2 + ys[i] - r.rand() * 40); cv2.circle(f, (px, py), int(1 + r.rand() * 2), accent, -1, cv2.LINE_AA)
def sink(f, s, name, size, x, y, t, t0, color=OFFW, a=1.0, track=0):
    u = (t - t0) / .55
    if u < 0: return
    k = eo(u); m = tex(s, name, size, track); sc = lerp(1.35, 1.0, k); put(f, m, x, y + 14, (0, 0, 0), a * .5 * k, sc, blur=16); put(f, m, x, y, color, a * clamp(u * 3), sc, blur=lerp(10, 0, k))
def wipe_title(f, s, name, size, x, y, t, t0, color=OFFW, a=1.0, track=0):
    u = eo((t - t0) / .35)
    if u <= 0: return
    m = tex(s, name, size, track); clip = np.zeros_like(m); w = m.shape[1]; clip[:, :max(int(w * u), 1)] = 1; clip = cv2.GaussianBlur(clip, (0, 0), 6)
    put(f, m * clip, x, y, color, a)
def label(f, x, y, s, t, t0, a=1.0):
    if t < t0: return
    k = clamp((t - t0) / .3) * a; put(f, tex(s, 'psb', 30, 2), x, y, (205, 205, 205), k * .9)
# ---- grade
def grade(fr):
    f = fr.astype(np.float32); g = f.mean(2, keepdims=True); f = g + (f - g) * .88; f = (f - 128) * 1.10 + 124; f[..., 0] *= 1.03; f[..., 2] *= 1.02
    return np.clip(f, 0, 255).astype(np.uint8)
# ---- captions
KEYS = {'interstellar', 'top', '5,', 'lost', 'plot.', 'rank', '3', 'pirates', 'pearl.', 'different', 'cinematography,', 'sound', 'dark', 'knight.', 'classic', 'solid', '1,', 'important', 'storytelling', 'characters.', 'bro,', 'bro.', 'cinematography,', 'level.', '2'}
def groups():
    g = []; cur = []
    for w in WORDS:
        cur.append(w)
        if len(cur) >= 3 or w[0][-1] in '.,?!' : g.append(cur); cur = []
    if cur: g.append(cur)
    return g
GROUPS = groups()
def captions(f, t, accent):
    for g in GROUPS:
        a0 = g[0][1] - .04; a1 = g[-1][2] + .22
        if a0 <= t < a1:
            u = clamp((t - a0) / .12); sc = lerp(1.12, 1.0, eo(u)); k = clamp((a1 - t) / .1)
            items = [(w[0].strip('.,').upper() if w[0].lower().strip('.,') in {x.strip('.,') for x in KEYS} else w[0].strip('.,').lower(), w[0].lower() in KEYS) for w in g]
            parts = []
            for s, key in items:
                nm, sz, col = ('anton', 112, accent) if key else ('psb', 60, OFFW); parts.append((s, nm, sz, col, twidth(s, nm, sz, 0)))
            tot = sum(p[4] for p in parts) + 26 * (len(parts) - 1)
            if tot > 960: sc *= 960 / tot; tot = 960
            x = 540 - tot * sc / 2 / (sc if False else 1)
            xx = 540 - (sum(p[4] for p in parts) + 26 * (len(parts) - 1)) * sc / 2
            for s, nm, sz, col, wd in parts:
                text(f, s, nm, sz, xx + wd * sc / 2, 1560, col, k * clamp(u * 3), sc=sc, shadow=.85); xx += (wd + 26) * sc
            return

# ---- film definitions
FILMS = [
 dict(key='pir', n=3, acc=TEAL, t0=7.08, dock=9.0, shrink=12.4, end=15.45, title=['PIRATES OF THE', 'CARIBBEAN'], sub='THE CURSE OF THE BLACK PEARL', meta='2003  -  GORE VERBINSKI', poster='pir_poster',
      pros=[(12.53, 'CINEMATOGRAPHY', ''), (13.31, 'SOUND DESIGN', ''), (14.03, 'EVERYTHING ON A DIFFERENT LEVEL', '')],
      bg=[(7.0, 10.6, 'pir_poster', 20, .38, 1.0, 1.25), (10.6, 15.5, 'pir_poster', 14, .42, 1.8, 2.1)], title_t=9.0),
 dict(key='tdk', n=2, acc=STEEL, t0=15.62, dock=16.5, shrink=16.45, end=21.0, title=['THE DARK', 'KNIGHT'], sub='', meta='2008  -  CHRISTOPHER NOLAN', poster='tdk_poster',
      pros=[(16.81, 'CLASSIC CHOICE', ''), (17.67, 'BEATS EVERY SINGLE THING', ''), (19.87, 'REALLY SOLID FILM', '')],
      bg=[(15.5, 21.1, 'tdk_tumbler', 0, .46, 1.0, 1.22)], title_t=16.1),
 dict(key='int', n=1, acc=AMBER, t0=21.58, dock=23.45, shrink=24.3, end=28.95, title=['INTERSTELLAR'], sub='', meta='2014  -  CHRISTOPHER NOLAN', poster='int_poster',
      pros=[(24.52, 'STORYTELLING', ''), (26.4, 'CINEMATOGRAPHY', ''), (27.18, 'SOUND DESIGN', ''), (28.0, 'CHARACTERS', '')],
      bg=[(21.1, 24.5, 'int_poster', 22, .40, 1.0, 1.3), (24.5, 26.3, 'int_end', 9, .5, 1.0, 1.25), (26.3, 27.15, 'int_ice', 0, .48, 1.0, 1.2), (27.15, 28.0, 'int_bh', 6, .5, 1.0, 1.2), (28.0, 29.0, 'int_poster', 22, .42, 1.0, 1.2)], title_t=23.05),
]
HOOK_BG = ('int_bh', 5, .55)
INTERLUDES = [(18.55, 19.55, 'tdk_tumbler', 'THE TUMBLER  -  EUROPEAN PREMIERE', 0), (26.42, 27.12, 'int_ice', 'FILMING LOCATION  -  ICELAND', 0), (27.2, 27.98, 'int_bh', 'GARGANTUA', 1)]
def film_at(t):
    for F in FILMS:
        if F['t0'] - 8 < t < F['end'] + .05 and F['key'] and ((F is FILMS[0] and 7.0 <= t < 15.5) or (F is FILMS[1] and 15.5 <= t < 21.1) or (F is FILMS[2] and 21.1 <= t < 28.95)): return F
    return None
def bg_layer(t):
    f = np.full((H, W, 3), CHAR, np.uint8); y = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]; f = (f.astype(np.float32) * (1.0 + .5 * (1 - y))).astype(np.uint8)
    if t < 3.5:
        k, bl, dm = HOOK_BG; a = bgimg(k, t, t / 3.5, bl, dm, AMBER, 1.05, 1.25); return a
    if t >= 28.95:
        return bgimg('int_poster', t, clamp((t - 28.95) / 5), 22, .34, AMBER, 1.2, 1.5)
    F = film_at(t)
    if F:
        for t0, t1, k, bl, dm, z0, z1 in F['bg']:
            if t0 <= t < t1:
                a = bgimg(k, t, (t - t0) / max(t1 - t0, .3), bl, dm, F['acc'], z0, z1); kk = sm((t - t0) / .3) if t0 > F['bg'][0][0] else sm((t - t0) / .4)
                f = (f.astype(np.float32) * (1 - kk) + a.astype(np.float32) * kk).astype(np.uint8)
    return f
def accent_at(t): return TEAL if 7 <= t < 15.5 else STEEL if 15.5 <= t < 21.1 else AMBER
def behind(f, t):
    if 0.82 <= t < 3.5:
        burn(f, 'INTERSTELLAR', 'anton', 172, 540, 600, (t - .82) / .9, t, AMBER)
        if t > 2.0: label(f, 540, 735, 'TOP 5?', t, 2.0)
    if 3.5 <= t < 7.0:
        burn(f, 'TOP 3', 'anton', 420, 540, 560, (t - 4.15) / .9, t, AMBER)
        if t > 4.7: wipe_title(f, 'BEST FILMS EVER MADE', 'anton', 82, 540, 800, t, 4.7)
    F = film_at(t)
    if F:
        u = t - F['t0']
        if 0 <= u < (F['dock'] - F['t0']) + .5:
            # ghost number + big poster behind me
            burn(f, str(F['n']), 'anton', 1100, 200, 760, (t - F['t0']) / .7, t, F['acc'], color=tuple(int(c * .55) for c in F['acc'])) if F['key'] == 'int' else sink(f, str(F['n']), 'anton', 1100, 200, 760, t, F['t0'], F['acc'], a=.35)
            big = 1.0 + .0; k = eo(u / .32); sc = lerp(1.7, 1.0, k); w = int(700 * sc)
            dk = clamp((t - F['dock']) / .5); e = eio(dk)
            cx = lerp(540, 195, e); cy = lerp(520, 330, e); w = int(lerp(w, 300, e)); im = cardimg(F['poster'], max(w, 60), (u - .25) / .45)
            paste(f, im, cx, cy, clamp(u / .12))
            if 0 <= u < .3: pass
        elif t >= F['dock'] + .5 and t < F['end']:
            im = cardimg(F['poster'], 300); paste(f, im, 195, 330, 1.0 if t < F['end'] - .25 else clamp((F['end'] - t) / .25))
def front_ui(f, t):
    F = film_at(t)
    if not F or t < F['dock'] - .1: return
    acc = F['acc']; out = clamp((F['end'] - t) / .25)
    if out <= 0: return
    x0 = 380; w = 640
    tt = t - F['title_t']
    big_until = F['shrink']; sh = eio((t - big_until) / .35)
    if F is FILMS[2] and t < big_until: pass
    # title block: big lines fade into a compact one-line header
    nl = len(F['title']); sz = 150 if nl == 2 else 118; step = sz * .88; ys = 210; big_a = out * (1 - sh)
    for i, ln in enumerate(F['title']):
        if F['key'] == 'int' and t < F['title_t'] + .8: break
        t_start = F['title_t'] + (.8 if F['key'] == 'int' else .12 * i)
        if t >= t_start and big_a > .01: wipe_title(f, ln, 'bebas', sz, x0 + w / 2, ys + i * step, t, t_start, OFFW, big_a, track=2)
    ym = ys + (nl - 1) * step + sz * .5 + 30
    if t >= F['title_t'] + .5 and sh < .9 and (F['key'] != 'int' or t >= F['title_t'] + 1.2): text(f, F['sub'] or F['meta'], 'psb', 30, x0 + w / 2, ym, acc, big_a * clamp((t - F['title_t'] - .5) / .3))
    if sh > .05:
        full = ' '.join(F['title']); hsz = 64
        while twidth(full, 'bebas', hsz, 2) > w and hsz > 30: hsz -= 2
        text(f, full, 'bebas', hsz, x0 + twidth(full, 'bebas', hsz, 2) / 2, 118, OFFW, out * sh, track=2, shadow=.6); text(f, F['meta'], 'psb', 24, x0 + twidth(F['meta'], 'psb', 24, 0) / 2, 168, GREY, out * sh)
    # pros
    n = len(F['pros']); y0 = 262; gap = 96
    if F['pros'] and t >= F['pros'][0][0] - .05:
        hk = clamp((t - F['pros'][0][0] + .05) / .3); cv2.line(f, (x0, 232), (x0 + int(w * eo((t - F['pros'][0][0] + .05) / .45)), 232), acc, 3, cv2.LINE_AA)
        text(f, f"WHY IT'S #{F['n']}", 'psb', 28, x0 + 95, 212, acc, hk * out)
    for i, (tp, lab, supp) in enumerate(F['pros']):
        u = (t - tp) / .38
        if u <= 0: continue
        k = eo(u); y = y0 + i * gap + 40; xo = int((1 - k) * 90 * (1 if i % 2 == 0 else -1) * .6)
        text(f, f'PRO {i + 1:02d}', 'psb', 24, x0 + 55 + xo, y - 26, acc, clamp(u * 2.5) * out)
        sz = 74; mw = w - 20
        while twidth(lab, 'bebas', sz, 1) > mw and sz > 38: sz -= 4
        text(f, lab, 'bebas', sz, x0 + twidth(lab, 'bebas', sz, 1) / 2 + xo, y + 14, OFFW, clamp(u * 2.5) * out, track=1, shadow=.8)
        cv2.line(f, (x0, y + 52), (x0 + int(mw * eo(u)), y + 52), (90, 90, 90), 1, cv2.LINE_AA)
def wipe_title_front(f, s, name, size, x, y, t, t0, color, a, tr=0):
    wipe_title(f, s, name, size, x, y, t, t0, color, a, track=tr)
def interlude(f, t):
    for a, b, k, lab, mode in INTERLUDES:
        if a <= t < b:
            u = (t - a) / (b - a); out = clamp((b - t) / .12) * clamp((t - a) / .1)
            if mode == 0: im = bgimg(k, t, u, 0, 1.0, (0, 0, 0), 1.05, 1.28)
            else:
                canvas = np.zeros((H, W, 3), np.uint8); card = cardimg(k, 1080); h = card.shape[0]; s = lerp(1.0, 1.12, u); card = cv2.resize(card, None, fx=s, fy=s); hh, ww = card.shape[:2]
                bgc = bgimg(k, t, u, 18, .45, AMBER, 1.0, 1.3); canvas[:] = bgc; y0 = H // 2 - hh // 2; x0 = max((W - ww) // 2, 0); canvas[y0:y0 + hh, x0:x0 + min(ww, W)] = card[:, :min(ww, W)] if ww <= W else card[:, (ww - W) // 2:(ww - W) // 2 + W]; im = canvas
            f[:] = (f.astype(np.float32) * (1 - out) + im.astype(np.float32) * out).astype(np.uint8)
            text(f, lab, 'psb', 34, 540, 1720, OFFW, out * clamp(u * 4)); return True
    return False
def endcard(f, t):
    u = clamp((t - VDUR + .1) / .5)
    if u <= 0: return
    f[:] = (f.astype(np.float32) * (1 - .8 * u)).astype(np.uint8)
    for i, (n_, s, c) in enumerate([('3', 'PIRATES OF THE CARIBBEAN', TEAL), ('2', 'THE DARK KNIGHT', STEEL), ('1', 'INTERSTELLAR', AMBER)]):
        k = clamp(u * 2 - i * .3); y = 820 + i * 150
        text(f, n_, 'anton', 120, 150, y, c, k); text(f, s, 'bebas', 92, 190 + twidth(s, 'bebas', 92, 1) / 2 + 60, y, OFFW, k, track=1)
    text(f, "IF IT'S NOT IN YOUR TOP 3", 'psb', 40, 540, 1300, GREY, clamp(u * 2 - .6)); text(f, "YOU'VE LOST THE PLOT", 'anton', 78, 540, 1380, OFFW, clamp(u * 2 - .8))
# ---- frame
def frame(k, fr, al):
    t = k / FPS; f = bg_layer(t); behind(f, t)
    z = 0.86
    for tp in (6.4, 14.85, 21.0):
        if tp <= t < tp + .7: z = .86 * (1 + .05 * eo((t - tp) / .7))
    g = grade(fr); a = prep_alpha(al); g2, a2 = spk(g, a, z, 540, 1920, 0, 0)
    sh = cv2.GaussianBlur(a2, (0, 0), 22); f = (f.astype(np.float32) * (1 - .42 * sh[..., None])).astype(np.uint8)
    acc = accent_at(t); rim = np.clip(a2 - cv2.erode(a2, np.ones((9, 9), np.uint8)), 0, 1); rim = cv2.GaussianBlur(rim, (0, 0), 3)
    g2 = np.clip(g2.astype(np.float32) + rim[..., None] * np.array(acc, np.float32) * .35, 0, 255).astype(np.uint8)
    f = over(f, g2, a2)
    gg = np.clip((np.arange(H, dtype=np.float32) - 1180) / 600, 0, 1)[:, None, None] * .62; f = (f.astype(np.float32) * (1 - gg)).astype(np.uint8)
    front_ui(f, t)
    il = interlude(f, t)
    if t < VDUR and not il: captions(f, t, acc)
    for tf in (F_['t0'] for F_ in FILMS):
        d = t - tf
        if 0 <= d < .24: f = cv2.addWeighted(f, 1, np.full_like(f, 255), .25 * (1 - d / .24), 0)
        if 0 <= d < .3:
            dx = int(14 * (1 - d / .3) ** 2 * math.sin(d * 120)); dy = int(10 * (1 - d / .3) ** 2 * math.cos(d * 140)); f = warp(f, np.float32([[1, 0, dx], [0, 1, dy]]))
    if t >= VDUR - .1: endcard(f, t)
    f = cv2.multiply(f, doc.vig(), scale=1 / 255); return cv2.addWeighted(f, 1, doc.grain(k), .04, -128 * .04)
def _chunk(args):
    a, b, out = args
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', '30', '-i', '-', '-c:v', 'libx264', '-crf', '15', '-preset', 'medium', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    last = None
    for k in range(a, b):
        i = min(k, int(VDUR * FPS) - 1) + 1
        fr = cv2.imread(f'{C4}/work/fr/{i:04d}.jpg'); al = cv2.imread(f'{C4}/work/al/{i:04d}.png', 0)
        enc.stdin.write(np.ascontiguousarray(frame(k, fr, al)).tobytes())
    enc.stdin.close(); enc.wait(); return out
def preview(ts, out):
    tiles = []
    for t in ts:
        k = int(t * FPS); i = min(k, int(VDUR * FPS) - 1) + 1; fr = cv2.imread(f'{C4}/work/fr/{i:04d}.jpg'); al = cv2.imread(f'{C4}/work/al/{i:04d}.png', 0); tiles.append(cv2.resize(frame(k, fr, al), (360, 640)))
    rows = [np.hstack(tiles[i:i + 6]) for i in range(0, len(tiles) - len(tiles) % 6, 6)]; cv2.imwrite(out, np.vstack(rows))
