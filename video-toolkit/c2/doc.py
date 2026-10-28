"""Documentary compositor: reporter-style edit. Speaker graded clip + RVM matte + real archival assets."""
import os, sys, json, math, random, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
R = os.path.dirname(os.path.abspath(__file__)); W, H, FPS = 1080, 1920, 30
RED = (44, 18, 205); OFFW = (226, 234, 238); CHAR = (24, 22, 22); GREYT = (150, 150, 150)
def clamp(x, a=0., b=1.): return a if x < a else b if x > b else x
def sm(x): x = clamp(x); return x * x * x * (x * (x * 6 - 15) + 10)
def eo(x): x = clamp(x); return 1 - (1 - x) ** 4
def eox(x): x = clamp(x); return 1 - 2 ** (-10 * x) if x < 1 else 1.0
def eio(x): x = clamp(x); return 3 * x * x - 2 * x ** 3
def back(x, s=1.4): x = clamp(x); return 1 + (s + 1) * (x - 1) ** 3 + s * (x - 1) ** 2
def lerp(a, b, u): return a + (b - a) * u

# ---------------------------------------------------------------- type
_F = {}; _T = {}; PAD = 28
FILES = {'bebas': 'BebasNeue.ttf', 'anton': 'Anton.ttf', 'inter': 'Inter.ttf', 'poppins': 'Poppins-ExtraBold.ttf'}
def font(name, size, w=600):
    k = (name, size, w)
    if k not in _F:
        f = ImageFont.truetype(f'{R}/fonts/{FILES[name]}', size)
        if name == 'inter':
            try:
                f.set_variation_by_axes([14 if 'opsz' in (a['name'].decode() if isinstance(a['name'], bytes) else a['name']).lower() else w for a in f.get_variation_axes()][:1] + [w])
            except Exception: pass
        _F[k] = f
    return _F[k]
def tex(s, name, size, track=0, w=600):
    k = (s, name, size, track, w)
    if k in _T: return _T[k]
    f = font(name, size, w)
    wd = int(f.getlength(s) + track * max(len(s) - 1, 0)) + 2 * PAD + 8; h = int(size * 1.6) + 2 * PAD
    im = Image.new('L', (wd, h), 0); d = ImageDraw.Draw(im)
    if track == 0: d.text((PAD, PAD), s, font=f, fill=255)
    else:
        x = PAD
        for c in s: d.text((x, PAD), c, font=f, fill=255); x += f.getlength(c) + track
    m = np.asarray(im, np.float32) / 255; ys = np.where(m.max(1) > .05)[0]; xs = np.where(m.max(0) > .05)[0]
    if len(ys) == 0: m = np.zeros((PAD * 2, PAD * 2), np.float32)
    else: m = np.ascontiguousarray(m[max(ys[0] - PAD, 0):ys[-1] + PAD, max(xs[0] - PAD, 0):xs[-1] + PAD])
    _T[k] = m; return m
def twidth(s, name, size, track=0, w=600): return tex(s, name, size, track, w).shape[1] - 2 * PAD
def put(cv, m, x, y, color=OFFW, a=1.0, sc=1.0, blur=0., dx=0, dy=0, add=False, clip=None, anchor='c'):
    if a <= .003 or sc <= .02: return
    if sc != 1: m = cv2.resize(m, None, fx=sc, fy=sc, interpolation=cv2.INTER_LINEAR)
    if blur > .3: m = cv2.GaussianBlur(m, (0, 0), blur)
    h, w = m.shape; x0 = int(round(x - (w / 2 if anchor == 'c' else PAD * sc) + dx)); y0 = int(round(y - h / 2 + dy))
    X0, Y0 = max(x0, 0), max(y0, 0); X1, Y1 = min(x0 + w, cv.shape[1]), min(y0 + h, cv.shape[0])
    if X0 >= X1 or Y0 >= Y1: return
    mm = m[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0] * a
    if clip is not None: mm = mm * clip[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0]
    roi = cv[Y0:Y1, X0:X1].astype(np.float32); mm3 = mm[..., None]; col = np.array(color, np.float32)
    roi = roi + col * mm3 if add else roi * (1 - mm3) + col * mm3
    cv[Y0:Y1, X0:X1] = np.clip(roi, 0, 255).astype(np.uint8)
def text(cv, s, name, size, x, y, color=OFFW, a=1.0, track=0, w=600, sc=1.0, shadow=0., **k):
    m = tex(s, name, size, track, w)
    if shadow > 0: put(cv, m, x, y, (0, 0, 0), a * shadow, sc, blur=10, dy=6 * sc, **k)
    put(cv, m, x, y, color, a, sc, **k)

# ---------------------------------------------------------------- images / grade helpers
IMG = {}
def load_assets():
    meta = json.load(open(f'{R}/assets/meta.json'))
    for k, v in meta.items(): IMG[k] = cv2.imread(v['file'])
    n = IMG['nyt']; sc = n.shape[1] / 1000
    IMG['nyt_front'] = n[int(18 * sc):int(642 * sc), int(198 * sc):int(975 * sc)].copy()
def tone(img, sat=.8, con=1.12, bright=0, tint=(0, 0, 0), gamma=1.0):
    f = img.astype(np.float32) / 255; g = f[..., 0] * .114 + f[..., 1] * .587 + f[..., 2] * .299
    f = g[..., None] + (f - g[..., None]) * sat; f = np.clip(f, 0, 1) ** gamma; f = (f - .5) * con + .5 + bright
    f = f + np.array(tint, np.float32)[None, None] / 255; return np.clip(f * 255, 0, 255).astype(np.uint8)
def warp(img, M, size=(W, H), interp=cv2.INTER_LINEAR): return cv2.warpAffine(img, M, size, flags=interp, borderMode=cv2.BORDER_REFLECT)
def kb(img, t, d, z0=1.0, z1=1.12, c0=(.5, .5), c1=(.5, .5), rot=0.0, interp=cv2.INTER_CUBIC):
    h, w = img.shape[:2]; base = max(W / w, H / h); u = eio(t / max(d, .01)); z = lerp(z0, z1, u); s = base * z
    cx = lerp(c0[0], c1[0], u) * w; cy = lerp(c0[1], c1[1], u) * h; cx = clamp(cx, W / 2 / s, w - W / 2 / s); cy = clamp(cy, H / 2 / s, h - H / 2 / s)
    M = np.float32([[s, 0, W / 2 - s * cx], [0, s, H / 2 - s * cy]])
    if rot:
        Rm = cv2.getRotationMatrix2D((W / 2, H / 2), rot, 1.0); M = (np.vstack([Rm, [0, 0, 1]]) @ np.vstack([M, [0, 0, 1]]))[:2].astype(np.float32)
    return warp(img, M, interp=interp)
_C = {}
def vig():
    if 'v' not in _C:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32); d = np.sqrt(((xx - W / 2) / (W * .70)) ** 2 + ((yy - H * .47) / (H * .58)) ** 2)
        _C['v'] = (np.repeat(np.clip(1.1 - .6 * d ** 2.1, .28, 1.0)[..., None], 3, 2) * 255).astype(np.uint8)
    return _C['v']
def grain(n):
    if 'g' not in _C:
        r = np.random.RandomState(11); _C['g'] = [cv2.GaussianBlur(r.randint(0, 255, (H, W, 3)).astype(np.uint8), (0, 0), .8) for _ in range(6)]
    return _C['g'][n % 6]
def botgrad():
    if 'bg' not in _C: _C['bg'] = (1 - np.clip((np.arange(H, dtype=np.float32) - 1180) / 520, 0, 1) * .55)[:, None, None]
    return _C['bg']
def darken_bottom(f): f[:] = (f.astype(np.float32) * botgrad()).astype(np.uint8)
def paper(t):
    if 'paper' not in _C:
        r = np.random.RandomState(5); n = cv2.GaussianBlur(r.rand(H // 4, W // 4).astype(np.float32), (0, 0), 1.2); n = cv2.resize(n, (W, H), interpolation=cv2.INTER_CUBIC)
        _C['paper'] = np.clip(18 + 14 * n, 0, 255).astype(np.uint8)
    p = _C['paper']; return np.repeat(p[..., None], 3, 2)

# ---------------------------------------------------------------- speaker + matte
def prep_alpha(a8):
    a = cv2.resize(a8, (W, H), interpolation=cv2.INTER_CUBIC).astype(np.float32) / 255; a = np.clip((a - .10) / .78, 0, 1); a = a * a * (3 - 2 * a)
    return cv2.GaussianBlur(a, (0, 0), 1.1)
def spk(fr, al, z=1.0, cx=540, cy=980, dx=0, dy=0):
    M = np.float32([[z, 0, cx - z * cx + dx], [0, z, cy - z * cy + dy]]); return warp(fr, M), cv2.warpAffine(al, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
def over(bg, fg, al): a = al[..., None]; return (bg.astype(np.float32) * (1 - a) + fg.astype(np.float32) * a).astype(np.uint8)
def behind_text(base, al, draw):
    tf = base.copy(); draw(tf); return over(tf, base, al)

# ---------------------------------------------------------------- graphic elements
def kin(f, s, name, size, x, y, t, t0, color=OFFW, hold=9.0, track0=36, w=600, shadow=.0, stagger=0.0, a=1.0, wide=False, maxw=1010):
    """Kinetic word: fast scale-down-to-size with tracking collapse, controlled stop, optional hard cut out."""
    p = (t - t0) / .22
    if p < 0 or t > t0 + hold: return
    while twidth(s, name, size, 0, w) * 1.12 > maxw: size -= 8
    p = clamp(p); sc = lerp(1.38, 1.0, back(p, 1.0)); tr = int(round(track0 * (1 - eo(p)) / 4) * 4)
    text(f, s, name, size, x, y, color, a * clamp(p * 4), track=tr, w=w, sc=sc, shadow=shadow)
def label(f, x, y, s, t, t0, a=1.0, dur=None, align='l'):
    """Documentary label: thin rule, small caps, typewriter reveal, red tick."""
    tt = t - t0
    if tt < 0: return
    if dur is not None and tt > dur: a *= 1 - clamp((tt - dur) / .25)
    if a <= .01: return
    n = int(clamp(tt * 42, 0, len(s))); sub = s[:n]
    wfull = twidth(s, 'inter', 24, 3, 600); rule = int(wfull * eo(tt / .45))
    xx = x if align == 'l' else x - wfull
    cv2.line(f, (xx, y - 24), (xx + rule, y - 24), (int(OFFW[0] * a), int(OFFW[1] * a), int(OFFW[2] * a)), 1, cv2.LINE_AA)
    cv2.rectangle(f, (xx, y - 24), (xx + 26, y - 21), RED, -1)
    if sub: put(f, tex(sub, 'inter', 24, 3, 600), xx, y + 2, OFFW, a, anchor='l')
def hud(f, t, items):
    """Ranking tracker top-left."""
    if t < 10.6: return
    a = sm((t - 10.6) / .5); x = 64; y0 = 118
    put(f, tex('EP 1', 'inter', 24, 3, 700), x, y0, LIME, a, anchor='l'); put(f, tex('THE WORST YEARS TO BE ALIVE', 'inter', 24, 3, 600), x + 62, y0, (190, 190, 190), a, anchor='l')
    cv2.line(f, (x, y0 + 22), (x + 330, y0 + 22), (90, 90, 90), 1, cv2.LINE_AA)
    for i, (n, label_, tt) in enumerate(items):
        if t < tt: continue
        u = clamp((t - tt) / .3); cur = t < (items[i + 1][2] if i + 1 < len(items) else 99)
        col = RED if cur else OFFW; yy = y0 + 70 + i * 62
        col = RED_HI if cur else OFFW; put(f, tex(str(n), 'bebas', 56, 2), x + 12, yy, col, a * u, anchor='l'); put(f, tex(label_, 'bebas', 56, 3), x + 58, yy, col, a * u * (1 if cur else .75), anchor='l', dx=(1 - eo(u)) * -18)
def whip(f, dt, strength=70):
    if dt >= .16: return f
    k = int(strength * (1 - dt / .16)); k += (k + 1) % 2
    if k < 3: return f
    return cv2.blur(f, (k, 1))
def flash(f, dt, amp=.35, dur=.22):
    if 0 <= dt < dur: f[:] = np.clip(f.astype(np.float32) + 255 * amp * (1 - dt / dur) ** 2, 0, 255).astype(np.uint8)
def shake(f, dt, amp=14, dur=.35):
    if not (0 <= dt < dur): return f
    r = random.Random(int(dt * 30)); k = amp * (1 - dt / dur) ** 2
    M = np.float32([[1, 0, r.uniform(-k, k)], [0, 1, r.uniform(-k, k)]]); return warp(f, M)
def rain(f, t, a=.5):
    rg = random.Random(7); lay = np.zeros((H, W), np.uint8)
    for i in range(240):
        x = rg.uniform(-100, W + 100); sp = rg.uniform(1500, 2400); ln = rg.uniform(60, 190); ph = rg.uniform(0, H + 300); y = (ph + t * sp) % (H + 300) - 150; sl = .14
        cv2.line(lay, (int(x), int(y)), (int(x - ln * sl), int(y + ln)), int(rg.uniform(90, 210)), 1 if rg.random() < .7 else 2, cv2.LINE_AA)
    lay = cv2.GaussianBlur(lay, (0, 0), .8).astype(np.float32) / 255 * a
    f[:] = np.clip(f.astype(np.float32) + lay[..., None] * np.array([235, 225, 215], np.float32) * .55, 0, 255).astype(np.uint8)
def card_persp(canvas, img, cx, cy, wd, t, t0, rot=-3.0, rise=520):
    """Document sliding in with perspective, soft shadow."""
    p = clamp((t - t0) / .55)
    if p <= 0: return
    e = eox(p); h = int(wd * img.shape[0] / img.shape[1]); k = .22 * (1 - e) + .035
    y = cy + (1 - e) * rise; ang = math.radians(rot * (1 - .35 * e) + (1 - e) * 6)
    pts = np.array([[-wd / 2, -h / 2], [wd / 2, -h / 2], [wd / 2, h / 2], [-wd / 2, h / 2]], np.float32)
    pts[0, 0] += wd * k; pts[1, 0] -= wd * k
    Rm = np.array([[math.cos(ang), -math.sin(ang)], [math.sin(ang), math.cos(ang)]], np.float32); dst = (pts @ Rm.T + np.array([cx, y], np.float32)).astype(np.float32)
    src = np.array([[0, 0], [img.shape[1], 0], [img.shape[1], img.shape[0]], [0, img.shape[0]]], np.float32)
    P = cv2.getPerspectiveTransform(src, dst); wi = cv2.warpPerspective(img, P, (W, H), flags=cv2.INTER_LINEAR)
    mk = cv2.warpPerspective(np.full(img.shape[:2], 255, np.uint8), P, (W, H), flags=cv2.INTER_LINEAR).astype(np.float32) / 255
    M2 = np.float32([[1, 0, 14], [0, 1, 26]]); sh = cv2.GaussianBlur(cv2.warpAffine(mk, M2, (W, H)), (0, 0), 22) * .75 * p
    a = canvas.astype(np.float32) * (1 - sh[..., None]); canvas[:] = (a * (1 - mk[..., None] * p) + wi.astype(np.float32) * (mk[..., None] * p)).astype(np.uint8)


# ---------------------------------------------------------------- episode title: EP 1 / RANKING THINGS THAT SHIFT (glitch editorial)
LIME = (0, 255, 190)   # BGR of electric lime (R190 G255 B0)
_T2 = {}
def tex2(s, name, size, track, lime):
    k = (s, name, size, track, tuple(sorted(lime)))
    if k in _T2: return _T2[k]
    f = font(name, size); adv = [f.getlength(c) for c in s]; wd = int(sum(adv) + track * (len(s) - 1)) + 2 * PAD + 8; h = int(size * 1.6) + 2 * PAD
    iw = Image.new('L', (wd, h), 0); il = Image.new('L', (wd, h), 0); dw = ImageDraw.Draw(iw); dl = ImageDraw.Draw(il); x = PAD
    for i, c in enumerate(s): (dl if i in lime else dw).text((x, PAD), c, font=f, fill=255); x += adv[i] + track
    mw = np.asarray(iw, np.float32) / 255; ml = np.asarray(il, np.float32) / 255; u = np.maximum(mw, ml)
    ys = np.where(u.max(1) > .05)[0]; xs = np.where(u.max(0) > .05)[0]; y0, y1, x0, x1 = max(ys[0] - PAD, 0), ys[-1] + PAD, max(xs[0] - PAD, 0), xs[-1] + PAD
    _T2[k] = (np.ascontiguousarray(mw[y0:y1, x0:x1]), np.ascontiguousarray(ml[y0:y1, x0:x1])); return _T2[k]
def title_masks(tl):
    cw = np.zeros((H, W, 3), np.uint8); cl = np.zeros((H, W, 3), np.uint8); r = random.Random(int(tl * 30) + 5)
    fade = 1.0 if tl < 1.55 else (0.0 if tl > 1.98 else (1 - sm((tl - 1.55) / .43)) * (1.0 if r.random() > .35 else .25))
    if tl >= .15 and fade > 0:
        k = int((tl - .15) * 30); on = tl > .46 or [1, 0, 1, 0, 0, 1, 1, 0, 1][min(k, 8)] == 1
        if on:
            put(cl, tex('EP 1', 'poppins', 64, 16), 540, 168, (255, 255, 255), fade)
            ru = int(150 * eo((tl - .2) / .4)); cv2.rectangle(cl, (540 - 150 - 60, 166), (540 - 150 - 60 + ru, 169), (255, 255, 255), -1); cv2.rectangle(cl, (540 + 210 - ru, 166), (540 + 210, 169), (255, 255, 255), -1)
    for s, name, size0, tr, lime, y, t0 in (('RANKING THINGS', 'bebas', 176, 8, {4, 10}, 300, .38), ('THAT SHIFT', 'anton', 236, 6, set(range(5, 10)), 478, .50)):
        p = clamp((tl - t0) / .34)
        if p <= 0 or fade <= 0: continue
        size = size0
        while twidth(s, name, size, tr) > 940: size -= 6
        track = tr + int(round(34 * (1 - eo(p)) / 6) * 6); mw, ml = tex2(s, name, size, track, lime); hh, ww = mw.shape
        edge = p * (ww + 80) - 40; clipx = np.clip((edge - np.arange(ww, dtype=np.float32)[None, :]) / 40, 0, 1) * np.ones((hh, 1), np.float32)
        flick = 1.0 if p >= 1 else .5 + .5 * random.Random(int(tl * 30) * 3 + len(s)).random()
        put(cw, mw, 540, y, (255, 255, 255), flick * fade, clip=clipx); put(cl, ml, 540, y, (255, 255, 255), flick * fade, clip=clipx)
    Mw = cw[..., 0].astype(np.float32) / 255; Ml = cl[..., 0].astype(np.float32) / 255
    if .38 <= tl < .9:
        k = int(34 * (1 - clamp((tl - .38) / .5))); k += (k + 1) % 2
        if k >= 3: Mw = cv2.blur(Mw, (k, 1)); Ml = cv2.blur(Ml, (k, 1))
    return Mw, Ml
def glitch_slices(f, s, seed):
    r = random.Random(seed); out = f.copy()
    for _ in range(r.randint(3, 7)):
        y = r.randint(0, H - 60); h = r.randint(16, int(40 + 110 * s)); dx = int(r.uniform(-1, 1) * (20 + 70 * s)); out[y:y + h] = np.roll(f[y:y + h], dx, axis=1)
    return out
def title_apply(f, al, tl):
    """f = live frame (speaker already composited); al = speaker alpha (title sits behind the head)."""
    dim = .80 + .20 * (1 - sm(clamp((tl - .12) / .25))) * 0 if False else 1 - .2 * sm(clamp((tl - .1) / .3)) * (1 - sm(clamp((tl - 1.6) / .35)))
    fd = (f.astype(np.float32) * dim).astype(np.uint8)
    Mw, Ml = title_masks(tl)
    split = 16 * (1 - eo(clamp((tl - .38) / .5))) ** 1.2 * (1 if tl >= .38 else 0) + (7 if 1.28 < tl < 1.37 else 0) + (24 * sm((tl - 1.55) / .4) if tl > 1.55 else 0); split = int(split)
    out = fd.astype(np.float32)
    for ch, dx in ((2, -split), (1, 0), (0, split)):
        mw = np.roll(Mw, dx, axis=1) if dx else Mw; ml = np.roll(Ml, dx, axis=1) if dx else Ml; cov = np.clip(mw + ml, 0, 1)
        out[..., ch] = out[..., ch] * (1 - cov) + OFFW[ch] * mw + LIME[ch] * ml
    res = over(out.astype(np.uint8), fd, al)
    s = 0.0
    if tl < .15: s = 1.0
    elif .38 <= tl < .62: s = .45
    elif 1.28 <= tl < 1.37: s = .22
    elif tl >= 1.55: s = .4 + .6 * sm((tl - 1.55) / .43)
    if s > 0:
        res = glitch_slices(res, s, int(tl * 30) + 17); k = int(10 * s)
        if k: res[..., 2] = np.roll(res[..., 2], k, axis=1); res[..., 0] = np.roll(res[..., 0], -k, axis=1)
        if tl >= 1.55: kb_ = int(46 * sm((tl - 1.55) / .43)); kb_ += (kb_ + 1) % 2; res = cv2.blur(res, (kb_, 1)) if kb_ >= 3 else res
    res[(np.arange(H) + int(tl * 60)) % 3 == 0] = (res[(np.arange(H) + int(tl * 60)) % 3 == 0].astype(np.float32) * .90).astype(np.uint8)
    return res

# ---------------------------------------------------------------- timeline
class S:
    def __init__(s, t0, t1, fn, caps=True, hud_=True): s.t0, s.t1, s.fn, s.caps, s.hud = t0, t1, fn, caps, hud_
SC = []
def scene(t0, t1, caps=True, hud_=True):
    def deco(fn): SC.append(S(t0, t1, fn, caps, hud_)); return fn
    return deco
TR = {}   # filled in setup: words
def kbimg(key, **kw): return kw
PHOTO = {}
def photos():
    if PHOTO: return PHOTO
    PHOTO['jus'] = tone(IMG['justinian'], .78, 1.15, -.02, (4, 6, 14)); PHOTO['pin'] = tone(IMG['pinatubo'], .62, 1.18, -.05, (6, 3, -6), gamma=1.15)
    PHOTO['fam'] = tone(IMG['famine'], .7, 1.2, -.12, (0, 2, 6), gamma=1.25); PHOTO['soup'] = tone(IMG['depression'], .0, 1.18, -.04, (4, 4, 6)); PHOTO['crash'] = tone(IMG['crash'], .0, 1.22, -.1, (2, 2, 4))
    PHOTO['lange'] = tone(IMG['migrant'], .0, 1.15, -.04, (4, 4, 6)); PHOTO['nyt'] = tone(IMG['nyt_front'], .55, 1.05, -.02, (-4, 2, 8)); return PHOTO

def build_scenes(words):
    SC.clear(); P = photos()
    # ---- 0.00-1.78  cold open: the claim, type behind head
    @scene(0.0, 1.80)
    def s1(tl, t, fr, al):
        z = lerp(1.0, 1.085, eio(tl / 1.8)); f, a = spk(fr, al, z)
        def d(c):
            kin(c, 'WORST', 'bebas', 560, 540, 650, t, .18, OFFW, w=600, track0=70)
            kin(c, 'THE', 'bebas', 120, 190, 380, t, .02, OFFW, track0=30); kin(c, 'YEAR', 'bebas', 210, 876, 395, t, .42, OFFW, track0=40)
        f = behind_text(f, a, d); darken_bottom(f); return f
    # ---- 1.80-3.50  "536 AD": text-zoom reveal into the Justinian mosaic
    @scene(1.80, 3.50, caps=False, hud_=False)
    def s2(tl, t, fr, al):
        img = kb(P['jus'], tl, 1.7, 1.02, 1.16, (.5, .36), (.5, .30)); fsp, asp = spk(fr, al, 1.085); base = (fsp.astype(np.float32) * .30).astype(np.uint8)
        m = tex('536', 'anton', 760, 6); h, w = m.shape; dist = cv2.distanceTransform((m > .5).astype(np.uint8), cv2.DIST_L2, 5); py, px = np.unravel_index(np.argmax(dist), dist.shape)
        f0 = math.exp(math.log(34) * eio(tl / .62)); sc = f0
        if tl < .68:
            mm = cv2.resize(m, None, fx=sc, fy=sc, interpolation=cv2.INTER_LINEAR); M = np.float32([[1, 0, 0], [0, 1, 0]])
            full = np.zeros((H, W), np.float32); x0 = int(W / 2 - px * sc); y0 = int(H / 2 - py * sc)
            X0, Y0 = max(x0, 0), max(y0, 0); X1, Y1 = min(x0 + mm.shape[1], W), min(y0 + mm.shape[0], H)
            if X1 > X0 and Y1 > Y0: full[Y0:Y1, X0:X1] = mm[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0]
            full = np.maximum(full, clamp((tl - .5) / .18) * 1.0); out = over(base, img, np.clip(full, 0, 1))
            return out
        out = img.copy(); g = np.clip((np.arange(H, dtype=np.float32) - 900) / 900, 0, 1)[:, None, None]; out = (out * (1 - g * .78)).astype(np.uint8)
        kin(out, '536', 'anton', 500, 345, 1370, t, 1.80 + .72, OFFW, track0=40, shadow=.5, maxw=560); kin(out, 'AD', 'bebas', 250, 800, 1410, t, 1.80 + .95, (70, 60, 235), track0=30)
        cv2.line(out, (64, 1215), (64 + int(520 * eo((tl - .9) / .5)), 1215), RED, 4, cv2.LINE_AA)
        label(out, 64, 1560, 'CONSTANTINOPLE  /  EMPEROR JUSTINIAN I  /  REIGNED 527-565', t, 1.80 + 1.0); return out
    # ---- 3.50-6.50  volcano: archival eruption behind the speaker (2.5D parallax)
    def volcano_bg(tl, dark=0.0):
        img = P['pin']; h, w = img.shape[:2]; base = max(W / w, H / h); u = eio(tl / 5.0)
        def layer(z, cy_n, cx_n):
            s = base * z; cx = clamp(cx_n * w, W / 2 / s, w - W / 2 / s); cy = clamp(cy_n * h, H / 2 / s, h - H / 2 / s); return np.float32([[s, 0, W / 2 - s * cx], [0, s, H / 2 - s * cy]])
        Ms = layer(lerp(1.0, 1.16, u), lerp(.56, .36, u), .47); Mg = layer(lerp(1.0, 1.30, u), lerp(.56, .44, u), .47)
        sky = warp(img, Ms, interp=cv2.INTER_CUBIC); gnd = warp(img, Mg, interp=cv2.INTER_CUBIC)
        yy = np.arange(h, dtype=np.float32); gm_src = np.repeat(np.clip((yy - .74 * h) / (.05 * h), 0, 1)[:, None], w, 1)
        gm = cv2.warpAffine(gm_src, Mg, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        bgf = over(sky, gnd, gm); return (bgf.astype(np.float32) * (1 - dark)).astype(np.uint8)
    @scene(3.50, 8.30)
    def s3(tl, t, fr, al):
        dark = sm((t - 6.45) / 1.15); bg = volcano_bg(tl, dark if t < 7.62 else 1.0)
        z = lerp(1.04, 1.12, eio(tl / 4.8)); f, a = spk(fr, al, z, dy=40)
        g = np.clip((np.arange(H, dtype=np.float32) - 1150) / 770, 0, 1)[:, None, None]; bg = (bg * (1 - g * .6)).astype(np.uint8)
        kin(bg, 'ERUPTION', 'anton', 330, 540, 640, t, 4.18, OFFW, hold=2.2, track0=60, shadow=.45)
        if t > 6.55:
            kin(bg, '18', 'anton', 420, 330, 300, t, 6.88, OFFW, hold=1.6, track0=0, shadow=.5); kin(bg, 'MONTH', 'bebas', 230, 760, 330, t, 7.12, OFFW, hold=1.4, track0=40)
            if t > 7.45: kin(bg, 'BLACKOUT', 'anton', 240, 540 + (random.Random(int(t * 30)).uniform(-6, 6) if t < 7.75 else 0), 540, t, 7.45, (70, 60, 235), hold=1.0, track0=20, shadow=.4)
        if t < 6.45: label(bg, 64, 1590, 'ILLUSTRATIVE  /  MOUNT PINATUBO ERUPTION, 1991  /  USGS', t, 3.9)
        tint = bg.astype(np.float32); out = over(bg, tone(f, .95, 1.0, 0, (0, 0, 0)), a)
        sh = cv2.GaussianBlur(a, (0, 0), 38) * .45; out = (out.astype(np.float32) * (1 - (sh * (1 - a))[..., None])).astype(np.uint8)
        darken_bottom(out); return out
    # ---- 8.30-13.60  series intro: face stays, restrained editorial layer
    @scene(8.30, 13.60)
    def s4(tl, t, fr, al):
        z = lerp(1.0, 1.07, eio(tl / 5.3)) * lerp(1.12, 1.0, eo(tl / .3)); f, a = spk(fr, al, z)
        def d(c): kin(c, 'RANKING', 'bebas', 470, 540, 640, t, 10.36, OFFW, hold=1.4, track0=60)
        f = behind_text(f, a, d); darken_bottom(f)
        if tl < 2.0: f = title_apply(f, a, tl)
        return f
    # ---- 13.60-15.80  NO. 2 / 1315: typographic card
    @scene(13.60, 15.80, caps=False)
    def s5(tl, t, fr, al):
        f = paper(t); kin(f, 'NO. 2', 'bebas', 190, 540, 660, t, 13.62, RED, track0=40)
        kin(f, '1315', 'anton', 820, 540, 1010, t, 14.68, OFFW, track0=30, shadow=.6); cv2.line(f, (84, 1380), (84 + int(912 * eo((t - 14.9) / .6)), 1380), RED, 5, cv2.LINE_AA)
        label(f, 64, 1590, 'EUROPE', t, 14.9); return f
    # ---- 15.80-18.60  Great Famine: illuminated manuscript full-screen
    @scene(15.80, 18.60, hud_=False)
    def s6(tl, t, fr, al):
        f = kb(P['fam'], tl, 2.8, 1.05, 1.22, (.5, .62), (.5, .40)); g = np.clip((np.arange(H, dtype=np.float32) - 1050) / 800, 0, 1)[:, None, None]; f = (f * (1 - g * .72)).astype(np.uint8)
        kin(f, 'FAMINE', 'anton', 360, 540, 1190, t, 16.08, RED, hold=1.32, track0=50, shadow=.6)
        kin(f, 'NO FOOD', 'anton', 330, 540, 1190, t, 17.45, OFFW, hold=1.1, track0=50, shadow=.6)
        label(f, 64, 1590, 'GREAT FAMINE  /  1315-1317  /  ILLUMINATED MANUSCRIPT, ERFURT', t, 15.95); return f
    # ---- 18.60-19.70  rainfall
    @scene(18.60, 19.72)
    def s7(tl, t, fr, al):
        z = lerp(1.03, 1.08, eio(tl / 1.1)); f, a = spk(fr, al, z)
        f = tone(f, .55, 1.12, -.05, (10, 4, -2))
        def d(c): kin(c, 'RAINFALL', 'bebas', 360, 540, 650, t, 18.95, OFFW, hold=1.0, track0=60); rain(c, t, .55)
        f = behind_text(f, a, d); rain(f, t + .13, .30); darken_bottom(f); return f
    # ---- 19.70-22.15  parents abandon kids: face, restraint
    @scene(19.70, 22.15)
    def s8(tl, t, fr, al):
        z = lerp(1.02, 1.12, eio(tl / 2.4)); f, a = spk(fr, al, z, dy=30); f = tone(f, .7, 1.08, -.03, (4, 2, 0)); darken_bottom(f)
        v = (vig().astype(np.float32) / 255); f = (f * (.55 + .45 * v)).astype(np.uint8); return f
    # ---- 22.15-23.25 / 23.25-24.05  the third: soup kitchen then Lange
    @scene(22.15, 23.25, hud_=False)
    def s9(tl, t, fr, al):
        f = kb(P['soup'], tl, 1.3, 1.08, 1.2, (.28, .52), (.55, .5)); g = np.clip((np.arange(H, dtype=np.float32) - 1000) / 900, 0, 1)[:, None, None]; f = (f * (1 - g * .75)).astype(np.uint8)
        kin(f, 'NO. 3', 'bebas', 210, 880, 330, t, 22.2, (70, 60, 235), track0=40, shadow=.5)
        label(f, 64, 1590, 'CHICAGO  /  FEB 1931  /  SOUP KITCHEN LINE  /  NARA', t, 22.3); return f
    @scene(23.25, 24.05, hud_=False)
    def s10(tl, t, fr, al):
        f = kb(P['lange'], tl, .85, 1.05, 1.16, (.52, .45), (.52, .40)); g = np.clip((np.arange(H, dtype=np.float32) - 1000) / 900, 0, 1)[:, None, None]; f = (f * (1 - g * .78)).astype(np.uint8)
        kin(f, 'THE GREAT', 'bebas', 170, 540, 1120, t, 23.2, OFFW, track0=40, shadow=.6); kin(f, 'DEPRESSION', 'anton', 250, 540, 1270, t, 23.45, OFFW, track0=40, shadow=.6)
        label(f, 64, 1590, 'DOROTHEA LANGE  /  MIGRANT MOTHER  /  1936', t, 23.35); return f
    # ---- 24.05-26.45  Wall Street crash: crowd + the real NYT front page
    @scene(24.05, 26.45, hud_=False)
    def s11(tl, t, fr, al):
        f = kb(P['crash'], tl, 2.4, 1.05, 1.22, (.5, .6), (.5, .45)); f = (f.astype(np.float32) * .52).astype(np.uint8)
        card_persp(f, P['nyt'], 540, 640, 940, t, 24.35, rot=-2.6)
        if t > 24.95:
            bx0, by0, bx1, by1 = 100, 640 - 335, 980, 640 - 335 + 255; p = clamp((t - 24.95) / .5)
            cv2.rectangle(f, (bx0, by0), (bx0 + int((bx1 - bx0) * p), by1), RED, 6, cv2.LINE_AA)
        g = np.clip((np.arange(H, dtype=np.float32) - 1100) / 700, 0, 1)[:, None, None]; f = (f * (1 - g * .7)).astype(np.uint8)
        kin(f, 'CRASHED', 'anton', 320, 540, 1230, t, 25.0, RED, hold=.62, track0=20, shadow=.7); kin(f, '1929', 'anton', 440, 540, 1240, t, 25.62, OFFW, track0=30, shadow=.7)
        label(f, 64, 1590, 'WALL STREET  /  OCTOBER 1929  /  NEW YORK TIMES, OCT 30', t, 24.2); return f
    # ---- 26.45-27.62  them days weren't fun
    @scene(26.45, 27.65)
    def s12(tl, t, fr, al):
        z = lerp(1.04, 1.13, eio(tl / 1.2)); f, a = spk(fr, al, z, dy=20); f = tone(f, .75, 1.1, -.04); darken_bottom(f)
        v = (vig().astype(np.float32) / 255); f = (f * (.5 + .5 * v)).astype(np.uint8); return f
    # ---- end card
    @scene(27.65, 29.0, caps=False, hud_=False)
    def s13(tl, t, fr, al):
        f = paper(t) // 2; a = sm(tl / .5)
        put(f, tex('RANKING THINGS THAT SHIFT   /   EP 1', 'inter', 26, 6, 600), 540, 660, LIME, a); put(f, tex('THE WORST YEARS TO BE ALIVE', 'bebas', 84, 5), 540, 760, OFFW, a); cv2.line(f, (300, 850), (300 + int(480 * eo((tl - .3) / .6)), 850), RED, 4, cv2.LINE_AA)
        for i, (n, l) in enumerate((('1', '536 AD'), ('2', '1315'), ('3', '1929'))):
            u = clamp((tl - .5 - i * .18) / .3); put(f, tex(n + '   ' + l, 'bebas', 96, 5), 540, 960 + i * 118, OFFW if i else RED, a * u, dy=(1 - eo(u)) * 20)
        return f
    return SC

# ---------------------------------------------------------------- captions (dialogue, documentary-style)
KEY = {'WORST', 'ERUPTION', 'BLACKOUT', 'MONTH', 'FAMINE', 'NO', 'FOOD', 'RAINFALL', 'ABANDON', 'KIDS', 'SURVIVE', 'DEPRESSION', 'CRASHED', "WEREN'T", 'FUN', 'RANKING', 'VOLCANO', '1315', '1929', '536', '18'}
def make_chunks(words):
    toks = [[w.strip('.,!?;:"').upper(), a, b, w.strip()[-1:] in ',.?!'] for w, a, b in words if w.strip('.,!?;:"')]
    for t in toks:
        if t[0] == 'TO' and abs(t[1] - 13.7) < .15: t[0] = 'TWO'
    ch = []; cur = []
    for t in toks:
        if cur:
            txt = ' '.join(x[0] for x in cur + [t])
            if len(cur) >= 4 or len(txt) > 22 or t[1] - cur[-1][2] > .35 or cur[-1][3]: ch.append(cur); cur = []
        cur.append(t)
    if cur: ch.append(cur)
    return ch
RED_HI = (72, 64, 238)
def draw_caps(f, chunks, t, scene_caps, y=1490):
    if not scene_caps: return
    for i, c in enumerate(chunks):
        t0 = c[0][1]; nxt = chunks[i + 1][0][1] if i + 1 < len(chunks) else c[-1][2] + .5; t1 = min(nxt, c[-1][2] + .55) if nxt - c[-1][2] > .5 else nxt
        if t < t0 or t >= t1: continue
        words = [x for x in c if t >= x[1] - .02]; size = 104; full = ' '.join(x[0] for x in c)
        while twidth(full, 'bebas', size, 3) > 940: size -= 6
        widths = [twidth(x[0], 'bebas', size, 3) for x in c]; gap = int(size * .26); total = sum(widths) + gap * (len(c) - 1); x0 = 540 - total / 2; xs = []
        cx = x0
        for wd in widths: xs.append(cx); cx += wd + gap
        for x, wd, xp in zip(c, widths, xs):
            if t < x[1] - .02: continue
            u = clamp((t - x[1]) / .12); key = x[0] in KEY; col = RED_HI if key else OFFW
            text(f, x[0], 'bebas', size, xp + wd / 2, y + (1 - eo(u)) * 16, col, clamp(u * 2.5), track=3, sc=1 + .14 * (1 - eo(u)), shadow=.95)

# ---------------------------------------------------------------- frame + driver
def frame_at(t, fr, a8, scenes, chunks):
    al = prep_alpha(a8); sc = next((s for s in scenes if s.t0 <= t < s.t1), scenes[-1]); f = sc.fn(t - sc.t0, t, fr, al)
    items = [(1, '536 AD', 10.9), (2, '1315', 14.9), (3, '1929', 23.4)]
    if sc.hud: hud(f, t, items)
    draw_caps(f, chunks, t, sc.caps)
    cuts = [3.5, 8.3, 13.6, 15.8, 18.6, 22.15, 23.25, 24.05, 26.45]
    for c in cuts:
        if 0 <= t - c < .16: f = whip(f, t - c, 60)
    for c in (1.9, 7.5, 14.68, 25.0): flash(f, t - c, .22 if c != 25.0 else .45)
    f = shake(f, t - 25.0, 16, .4); f = shake(f, t - 14.68, 8, .3)
    f = cv2.multiply(f, vig(), scale=1 / 255)
    fade = clamp((29.0 - t) / .5); f = (f.astype(np.float32) * fade).astype(np.uint8) if t > 28.5 else f
    return cv2.addWeighted(f, 1, grain(int(t * 30)), .045, -128 * .045)
def _fr(path, t0, n, w, h, pix):
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', f'{t0:.3f}', '-i', path, '-frames:v', str(n), '-f', 'rawvideo', '-pix_fmt', pix, '-'], stdout=subprocess.PIPE, bufsize=w * h * 3 * 3)
    sz = w * h * (3 if pix == 'bgr24' else 1)
    while True:
        b = p.stdout.read(sz)
        if len(b) < sz: break
        yield np.frombuffer(b, np.uint8).reshape(h, w, 3) if pix == 'bgr24' else np.frombuffer(b, np.uint8).reshape(h, w)
    p.wait()
def setup():
    load_assets(); cap = json.load(open(f'{R}/work/cap.json')); scenes = build_scenes(cap['words']); chunks = make_chunks(cap['words']); return scenes, chunks, cap['dur']
def get_frames(t0, n):
    last_f = None; last_a = None
    vid = _fr(f'{R}/work/clipg.mkv', t0, n, W, H, 'bgr24'); alp = _fr(f'{R}/work/alpha.mkv', t0, n, 540, 960, 'gray')
    for k in range(n):
        try: last_f = next(vid)
        except StopIteration: pass
        try: last_a = next(alp)
        except StopIteration: pass
        yield last_f, last_a
def _chunk(args):
    k, a, b = args; scenes, chunks, dur = setup(); out = f'{R}/work/dch_{k:03d}.mkv'
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', '30', '-i', '-', '-c:v', 'libx264', '-crf', '14', '-preset', 'fast', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    n = a
    for fr, a8 in get_frames(min(a / FPS, 27.5), b - a):
        enc.stdin.write(np.ascontiguousarray(frame_at(n / FPS, fr, a8, scenes, chunks)).tobytes()); n += 1
    enc.stdin.close(); enc.wait(); return out
def render(out_silent, chunk=90, procs=4):
    import multiprocessing as mp
    scenes, chunks, dur = setup(); total = int(29.0 * FPS); jobs = [(k, a, min(a + chunk, total)) for k, a in enumerate(range(0, total, chunk))]
    with mp.Pool(procs) as pool: outs = pool.map(_chunk, jobs, chunksize=1)
    open(f'{R}/work/dlist.txt', 'w').write(''.join(f"file '{o}'\n" for o in outs))
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'{R}/work/dlist.txt', '-c', 'copy', out_silent], check=True)
    for o in outs: os.remove(o)
def preview(ts, out, cols=6):
    scenes, chunks, dur = setup(); ims = []
    for t in ts:
        fr, a8 = next(get_frames(min(t, 27.5), 1)); ims.append(cv2.resize(frame_at(t, fr, a8, scenes, chunks), (360, 640), interpolation=cv2.INTER_AREA))
    rows = [np.hstack(ims[i:i + cols] + [np.zeros_like(ims[0])] * (cols - len(ims[i:i + cols]))) for i in range(0, len(ims), cols)]; cv2.imwrite(out, np.vstack(rows))
if __name__ == '__main__':
    if sys.argv[1] == 'pv': preview([float(x) for x in sys.argv[3:]], sys.argv[2])
    elif sys.argv[1] == 'render': render(sys.argv[2])
