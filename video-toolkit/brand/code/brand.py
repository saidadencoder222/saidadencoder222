"""/brand: the user's visual identity, copied from the inspo reel ("Grow to 50,000 using copywriting secrets").
Acid-yellow (RGB 242,244,16) + white on the real, unretouched room. Three typefaces: condensed serif (Instrument Serif) for the hero word, tight bold grotesk (Inter 700, tracking -3%) for captions, serif italic for accent words.
Captions are a single stream: plain white at the top of the frame, WHITE PILL with black text when an image is on screen; key words turn acid yellow. Images are unframed (paper/ads/screens/stock), a little rotated, no border, instant cut."""
import sys, math, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
import simple                                    # sets up the shared font dir
from simple import *
FDIR = simple.C2 + '/fonts'
YEL = (16, 244, 242); WH = (255, 255, 255); BLK = (10, 10, 10)          # BGR
FONTS = {'serif': 'InstrumentSerif-Regular.ttf', 'serifi': 'InstrumentSerif-Italic.ttf', 'sans': 'Inter.ttf'}
_F = {}
def pf(kind, size, w=700):
    k = (kind, size, w)
    if k not in _F:
        f = ImageFont.truetype(f'{FDIR}/{FONTS[kind]}', size)
        if kind == 'sans':
            try: f.set_variation_by_axes([14 if 'opsz' in (a['name'].decode() if isinstance(a['name'], bytes) else a['name']).lower() else w for a in f.get_variation_axes()][:1] + [w])
            except Exception:
                try: f.set_variation_by_axes([w])
                except Exception: pass
        _F[k] = f
    return _F[k]
_M = {}
def tm(s, kind, size, w=700, track=0.0, cx=1.0):
    """fixed-baseline text mask: (mask, advance_width). Same baseline for every word, so mixed colours/sizes line up."""
    key = (s, kind, size, w, track, cx)
    if key in _M: return _M[key]
    f = pf(kind, size, w); PADX = 24; H = int(size * 1.7); base = int(size * 1.2)
    adv = f.getlength(s) + track * max(len(s) - 1, 0)
    im = Image.new('L', (int(adv) + 2 * PADX + 4, H), 0); d = ImageDraw.Draw(im)
    if track == 0: d.text((PADX, base), s, font=f, fill=255, anchor='ls')
    else:
        x = PADX
        for c in s: d.text((x, base), c, font=f, fill=255, anchor='ls'); x += f.getlength(c) + track
    m = np.asarray(im, np.float32) / 255
    if cx != 1.0: m = cv2.resize(m, (max(int(m.shape[1] * cx), 4), m.shape[0]), interpolation=cv2.INTER_AREA); adv = adv * cx; PADX = PADX * cx
    _M[key] = (m, adv, base, PADX); return _M[key]
def blit(f, m, x, base_y, base, color, a=1.0, blur=0., dy=0, add=False, sc=1.0):
    if a <= .003: return
    if sc != 1: m = cv2.resize(m, None, fx=sc, fy=sc, interpolation=cv2.INTER_LINEAR); base = base * sc
    if blur > .3: m = cv2.GaussianBlur(m, (0, 0), blur)
    h, w = m.shape; x0 = int(round(x)); y0 = int(round(base_y - base + dy))
    X0, Y0 = max(x0, 0), max(y0, 0); X1, Y1 = min(x0 + w, 1080), min(y0 + h, f.shape[0])
    if X0 >= X1 or Y0 >= Y1: return
    mm = (m[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0] * a)[..., None]; roi = f[Y0:Y1, X0:X1].astype(np.float32); col = np.array(color, np.float32)
    roi = roi + col * mm if add else roi * (1 - mm) + col * mm; f[Y0:Y1, X0:X1] = np.clip(roi, 0, 255).astype(np.uint8)
def fit(kind, texts, size, maxw, w=700, track_k=-.03, cx=1.0):
    while sum(tm(t, kind, size, w, track_k * size, cx)[1] for t in texts) > maxw and size > 24: size -= 2
    return size
# ------------------------------------------------------------------------------------------------------------------ captions
def caption(f, words, y, hi=(), pill=False, a=1.0, size=64, cx=540, u=1.0):
    """one caption chunk, plain white (key words acid yellow) with a soft DARK shadow; no box. words rise + settle one after another (u = seconds since the chunk started)"""
    def width(sz): return sum(tm(w, 'sans', sz, 700, -.03 * sz)[1] for w in words) + .27 * sz * (len(words) - 1)
    while width(size) > 900 and size > 30: size -= 2
    tr = -.03 * size; sp = .27 * size; total = width(size); cx = min(max(cx, total / 2 + 40), 1040 - total / 2); x = cx - total / 2
    for i, wd in enumerate(words):
        m, adv, base, PADX = tm(wd, 'sans', size, 700, tr); ui = clamp((u - i * .045) / .16); e = 1 - (1 - ui) ** 3; yy = y + (1 - e) * 26; ai = a * min(ui * 4, 1)
        blit(f, m, x - PADX, yy, base, (0, 0, 0), ai * .5, blur=9, dy=5); blit(f, m, x - PADX, yy, base, YEL if i in hi else WH, ai)
        x += adv + sp
# ------------------------------------------------------------------------------------------------------------------ hero title (neon-yellow condensed serif + small white caps)
def title(f, big, sub, y=420, a=1.0, maxw=900):
    sz = fit('serif', [big], 300, maxw, 400, -.02, .78); m, adv, base, PADX = tm(big, 'serif', sz, 400, -.02 * sz, .78); x = 540 - adv / 2 - PADX
    blit(f, m, x, y, base, YEL, a * .85, blur=14, add=True); blit(f, m, x, y, base, YEL, a * .5, blur=5, add=True)       # neon glow
    blit(f, m, x, y, base, (200, 250, 250), a)                                                                         # hot core
    blit(f, m, x, y, base, YEL, a * .9)
    ss = fit('sans', [sub], 44, maxw - 60, 600, 0.0); tr = .09 * ss; m2, adv2, base2, PADX2 = tm(sub, 'sans', ss, 600, tr); x2 = 540 - adv2 / 2 - PADX2
    blit(f, m2, x2, y + 82, base2, (70, 70, 255), a * .6, blur=7, add=True); blit(f, m2, x2, y + 82, base2, WH, a)
# ------------------------------------------------------------------------------------------------------------------ typographic caption stack (hero word / white line / italic accent)
def stack(f, big, line, accent, y=360, a=1.0, size=140, u=None):
    sz = fit('serif', [big], size, 900, 400, -.015, .8); m, adv, base, PADX = tm(big, 'serif', sz, 400, -.015 * sz, .8)
    if u is not None and u < .45: m = m.copy(); m[:, int(ease(u / .35) * m.shape[1]):] = 0                                   # hero word wipes in from the left
    blit(f, m, 540 - adv / 2 - PADX, y, base, (0, 0, 0), a * .3, blur=9, dy=6); blit(f, m, 540 - adv / 2 - PADX, y, base, YEL, a)
    if u is not None and u > .2:                                                                                                  # yellow underline draws itself
        r_ = ease((u - .2) / .35); x0_ = 540 - adv * .36; cv2.line(f, (int(x0_), int(y + 26)), (int(x0_ + adv * .72 * r_), int(y + 26 + 3 * math.sin(r_ * 6))), YEL, 3, cv2.LINE_AA)
    if line:
        ls = fit('sans', [line], 56, 940, 700, -.03); m2, adv2, base2, P2 = tm(line, 'sans', ls, 700, -.03 * ls)
        blit(f, m2, 540 - adv2 / 2 - P2, y + 92, base2, (0, 0, 0), a * .38, blur=7, dy=4); blit(f, m2, 540 - adv2 / 2 - P2, y + 92, base2, WH, a)
    if accent:
        as_ = fit('serifi', [accent], 70, 700, 400, 0); m3, adv3, base3, P3 = tm(accent, 'serifi', as_, 400, 0)
        cx3 = min(800, 1040 - adv3 / 2); blit(f, m3, cx3 - adv3 / 2 - P3, y + 172, base3, (0, 0, 0), a * .38, blur=7, dy=4); blit(f, m3, cx3 - adv3 / 2 - P3, y + 172, base3, WH, a)
# ------------------------------------------------------------------------------------------------------------------ images: unframed, slightly rotated, instant
def ease(x): x = clamp(x); return 1 - (1 - x) ** 3
def paper(f, img, cx, cy, w, rot=0.0, shadow=.28, reveal=1.0, dy=0):
    cy = cy + dy
    h = int(img.shape[0] * w / img.shape[1]); r = cv2.resize(img, (int(w), h), interpolation=cv2.INTER_AREA if w < img.shape[1] else cv2.INTER_CUBIC)
    rgba = np.dstack([r[..., :3], np.full((h, int(w)), 255, np.uint8)])
    if reveal < 1.0: rgba[:, int(reveal * int(w)):, 3] = 0
    M = cv2.getRotationMatrix2D((w / 2, h / 2), rot, 1.0); cw = int(abs(w * math.cos(math.radians(rot))) + abs(h * math.sin(math.radians(rot)))) + 4; ch = int(abs(h * math.cos(math.radians(rot))) + abs(w * math.sin(math.radians(rot)))) + 4
    M[0, 2] += (cw - w) / 2; M[1, 2] += (ch - h) / 2; c = cv2.warpAffine(rgba, M, (cw, ch), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0, 0))
    x0, y0 = int(cx - cw / 2), int(cy - ch / 2); X0, Y0, X1, Y1 = max(x0, 0), max(y0, 0), min(x0 + cw, 1080), min(y0 + ch, f.shape[0])
    if X0 >= X1 or Y0 >= Y1: return
    sub = c[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0]; a = sub[..., 3:4].astype(np.float32) / 255
    sh = cv2.GaussianBlur(a[..., 0], (0, 0), 10)[..., None] * shadow; roi = f[Y0:Y1, X0:X1].astype(np.float32) * (1 - np.roll(sh, 8, 0))
    f[Y0:Y1, X0:X1] = np.clip(roi * (1 - a) + sub[..., :3].astype(np.float32) * a, 0, 255).astype(np.uint8)
# ------------------------------------------------------------------------------------------------------------------ grade (warm, clean, high quality; background stays the real room)
def grade_brand(raw):
    import grade51 as G
    f = G.warm_grade(raw).astype(np.float32) / 255
    lum = (f[..., 0] * .114 + f[..., 1] * .587 + f[..., 2] * .299)[..., None]
    bl = cv2.GaussianBlur(np.clip(f - .7, 0, 1) * 3.0, (0, 0), 20); f = 1 - (1 - f) * (1 - bl * .18)                    # soft highlight bloom
    f = f * np.array([.985, 1.0, 1.03], np.float32)                                                                       # a touch warmer
    f = np.power(np.clip(f, 0, 1), .94)                                                                                   # skin and room a little brighter
    H, W = f.shape[:2]; yy, xx = np.mgrid[0:H, 0:W].astype(np.float32); d = ((xx - W / 2) / (W * .8)) ** 2 + ((yy - H * .5) / (H * .75)) ** 2
    f = f * (1 - .10 * np.clip(d, 0, 1))[..., None]
    return np.clip(f * 255, 0, 255).astype(np.uint8)
# ------------------------------------------------------------------------------------------------------------------ framing: speaker lower in frame with headroom (like the inspo)
def frame_speaker(fr, S=.84, zoom=1.0):
    """scale the footage a little (anchored bottom-centre) so there is headroom for the title / images; the thin side strips continue the real wall (edge replicate, softened) and the top continues the wall tone"""
    h, w = fr.shape[:2]; sc = cv2.resize(fr, (int(w * S), int(h * S)), interpolation=cv2.INTER_AREA); sh, sw = sc.shape[:2]; x0 = (1080 - sw) // 2; y0 = 1920 - sh
    can = np.zeros((1920, 1080, 3), np.uint8); can[y0:, x0:x0 + sw] = sc
    L = cv2.GaussianBlur(np.repeat(sc[:, :1], x0, 1), (0, 0), 6); can[y0:, :x0] = L; rw = 1080 - x0 - sw; R = cv2.GaussianBlur(np.repeat(sc[:, -1:], rw, 1), (0, 0), 6); can[y0:, x0 + sw:] = R
    row = cv2.GaussianBlur(can[y0 + 4:y0 + 30].mean(0, keepdims=True), (0, 0), 50); can[:y0] = np.repeat(row, y0, 0).astype(np.uint8)
    if zoom != 1.0: can = cv2.warpAffine(can, np.float32([[zoom, 0, 540 - zoom * 540], [0, zoom, 1500 - zoom * 1500]]), (1080, 1920), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return can

# ------------------------------------------------------------------------------------------------------------------ motion graphics (brand-consistent: yellow / white, thin lines, no bounce)
def numeral(f, n, u, x=60, y=880, size=250):
    """countdown numeral in the condensed yellow serif on the left edge, slides in, with a thin line that draws under it"""
    m, adv, base, PADX = tm(str(n), 'serif', size, 400, 0, .8); sl = (1 - ease(u / .3)) * -70; a = ease(u / .25)
    blit(f, m, x + sl - PADX, y, base, (0, 0, 0), a * .3, blur=9, dy=6); blit(f, m, x + sl - PADX, y, base, YEL, a)
    r = ease((u - .15) / .45)
    if r > 0: cv2.line(f, (int(x + sl), int(y + 24)), (int(x + sl + 120 * r), int(y + 24)), YEL, 3, cv2.LINE_AA)
    ms, a2, b2, P2 = tm('HABIT', 'sans', 30, 700, 3.5); blit(f, ms, x + sl - P2, y - size * .78, b2, WH, a * .9)
def meter(f, frac, label, x=1040, y0=560, y1=1480):
    """thin vertical gauge on the right edge: white track, yellow fill, small rotated caps label"""
    ov = f.copy(); cv2.line(ov, (x, y0), (x, y1), (255, 255, 255), 6, cv2.LINE_AA); f[:] = cv2.addWeighted(ov, .28, f, .72, 0)
    yt = int(y1 - (y1 - y0) * clamp(frac)); cv2.line(f, (x, y1), (x, yt), YEL, 6, cv2.LINE_AA); cv2.circle(f, (x, yt), 11, YEL, -1, cv2.LINE_AA)
    ms, adv, base, PADX = tm(label, 'sans', 30, 700, 4.0); mm = cv2.rotate(ms[:, int(PADX * .5):int(PADX + adv + PADX * .5)], cv2.ROTATE_90_COUNTERCLOCKWISE); h, w = mm.shape
    x0 = x - w - 14; y0_ = y0 - h - 10
    if x0 > 0 and y0_ > 0:
        roi = f[y0_:y0_ + h, x0:x0 + w].astype(np.float32); a_ = mm[..., None]; f[y0_:y0_ + h, x0:x0 + w] = np.clip(roi * (1 - a_) + 255 * a_, 0, 255).astype(np.uint8)
def ring_pulse(f, cx, cy, u, r0=60, r1=330):
    if 0 <= u < .8:
        r = int(r0 + (r1 - r0) * ease(u / .8)); a = (1 - u / .8) * .7; ov = f.copy(); cv2.circle(ov, (int(cx), int(cy)), r, YEL, 3, cv2.LINE_AA); f[:] = cv2.addWeighted(ov, a, f, 1 - a, 0)

# ------------------------------------------------------------------------------------------------------------------ line-art motion graphics (yellow/white, drawn on)
def _poly(f, pts, col, th, a=1.0):
    ov = f.copy(); cv2.polylines(ov, [np.array(pts, np.int32)], False, col, th, cv2.LINE_AA); f[:] = cv2.addWeighted(ov, a, f, 1 - a, 0)
def g_write(f, x, y, u, w=260):
    for i in range(3):
        r = ease((u - i * .22) / .6)
        if r > 0: pts = [(x + k * w * r / 20, y + i * 46 + 9 * math.sin(k * 1.1 + i)) for k in range(21)]; _poly(f, pts, YEL if i == 0 else WH, 5, .95 if i == 0 else .7)
    if u > .1: cv2.circle(f, (int(x + w * ease((u - .6) / .6) * .9), int(y + 46 * 2 + 14)), 10, YEL, -1, cv2.LINE_AA)
def g_path(f, x, y, u, w=300, h=220):
    pts = [(x + w * p, y + h * (.5 + .45 * math.sin(p * 5.2 + .6)) - h * .5 * p) for p in np.linspace(0, 1, 60)]; n = int(60 * ease(u / 1.4))
    for i in range(0, max(n, 1), 3): cv2.circle(f, (int(pts[i][0]), int(pts[i][1])), 5, WH, -1, cv2.LINE_AA)
    if n > 0: cv2.circle(f, (int(pts[min(n, 59)][0]), int(pts[min(n, 59)][1])), 14, YEL, -1, cv2.LINE_AA)
def g_ripple(f, x, y, u, n=4):
    for i in range(n):
        v = ((u * .9) - i * .22) % 1.0
        if u * .9 - i * .22 >= 0: r = int(24 + 150 * v); a = (1 - v) * .85; ov = f.copy(); cv2.circle(ov, (int(x), int(y)), r, YEL if i % 2 == 0 else WH, 4, cv2.LINE_AA); f[:] = cv2.addWeighted(ov, a, f, 1 - a, 0)
    cv2.circle(f, (int(x), int(y)), 14, YEL, -1, cv2.LINE_AA)
def g_burst(f, x, y, u, n=14):
    for i in range(n):
        ang = i * 2 * math.pi / n + .2; v = ease(u / .7); r0 = 40 + 40 * v; r1 = r0 + (30 + 120 * v) * (1 if i % 2 else .6); a = 1 - clamp((u - .5) / .8)
        if a > 0: ov = f.copy(); cv2.line(ov, (int(x + math.cos(ang) * r0), int(y + math.sin(ang) * r0)), (int(x + math.cos(ang) * r1), int(y + math.sin(ang) * r1)), YEL if i % 3 else WH, 5, cv2.LINE_AA); f[:] = cv2.addWeighted(ov, a, f, 1 - a, 0)
def g_target(f, x, y, u):
    for i, r in enumerate((150, 100, 52)):
        v = ease((u - i * .12) / .35)
        if v > 0: ov = f.copy(); cv2.circle(ov, (int(x), int(y)), int(r * (2 - v)), YEL if i == 2 else WH, 5, cv2.LINE_AA); f[:] = cv2.addWeighted(ov, v * .9, f, 1 - v * .9, 0)
    v = ease((u - .4) / .3)
    if v > 0:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)): cv2.line(f, (int(x + dx * 168), int(y + dy * 168)), (int(x + dx * (168 - 52 * v)), int(y + dy * (168 - 52 * v))), YEL, 5, cv2.LINE_AA)
def g_ceiling(f, x, y, u, w=300):
    cv2.line(f, (int(x), int(y)), (int(x + w), int(y)), WH, 5, cv2.LINE_AA)
    h = 190 * ease(u / .9); cv2.rectangle(f, (int(x + 40), int(y + 200 - h)), (int(x + 120), int(y + 200)), YEL, -1, cv2.LINE_AA)
    if u > .9: cv2.rectangle(f, (int(x + 40), int(y + 10 + 190 * 0)), (int(x + 120), int(y + 200)), YEL, 3, cv2.LINE_AA)
    r = ease((u - .9) / .4)
    if r > 0: cv2.line(f, (int(x + 170), int(y + 200)), (int(x + 170 + 100 * r), int(y + 200 - 190 * r)), WH, 5, cv2.LINE_AA)
def g_loop(f, x, y, u):
    n = int(90 * ease(u / 1.6)); pts = [(x + (70 + 3 * k * .5) * math.cos(k * .14) * .9, y + (70 + 3 * k * .5) * math.sin(k * .14) * .9) for k in range(n)]
    if len(pts) > 1: _poly(f, pts, YEL, 5, .95)
def g_check(f, x, y, u):
    r = ease(u / .4); cv2.circle(f, (int(x), int(y)), int(70 * r), YEL, 6, cv2.LINE_AA)
    v = ease((u - .3) / .35)
    if v > 0: p = [(x - 30, y), (x - 8, y + 24), (x + 34, y - 26)]; _poly(f, p[:2] + [(p[1][0] + (p[2][0] - p[1][0]) * v, p[1][1] + (p[2][1] - p[1][1]) * v)], WH, 8)

# =========================================================== v3: measured from the "You're Too Smart To Grow" inspo (final; supersedes the earlier title/stack) ===========================
def title2(f, big, sub, y=1530, a=1.0, maxw=820):
    """hero title: mixed-case yellow condensed serif (no neon), white sans CAPS line under it. Sits low, over the torso, under the chin."""
    sz = fit('serif', [big], 230, maxw, 400, -.02, .8); m, adv, base, PADX = tm(big, 'serif', sz, 400, -.02 * sz, .8); x = 540 - adv / 2 - PADX
    blit(f, m, x, y, base, (0, 0, 0), a * .55, blur=14, dy=7); blit(f, m, x, y, base, YEL, a)
    ss = fit('sans', [sub], 62, 960, 600, -.01); m2, adv2, base2, P2 = tm(sub, 'sans', ss, 600, -.01 * ss); x2 = 540 - adv2 / 2 - P2
    blit(f, m2, x2, y + 100, base2, (0, 0, 0), a * .55, blur=9, dy=5); blit(f, m2, x2, y + 100, base2, WH, a)
def accent(f, word, x, y, u, size=190, glow=False, white_above=None, white_below=None, a=1.0):
    """big yellow serif word with an oversized italic swash capital (the inspo's 'Destroyed', 'Betrayed', 'Downfall'), small white sans lines above / below"""
    if u < 0: return
    a = a * clamp(u / .12); first, rest = word[0], word[1:]
    mF, advF, baseF, PF = tm(first, 'serifi', int(size * 1.35), 400, 0); mR, advR, baseR, PR = tm(rest, 'serif', size, 400, -.015 * size, .8)
    total = advF * .82 + advR; x0 = x - total / 2
    slide = (1 - ease(u / .3)) * 40
    for off, col, al, bl in ((0, YEL, a, 0.0),):
        if glow: blit(f, mF, x0 - PF + slide, y, baseF, YEL, a * .9, blur=16, add=True); blit(f, mR, x0 + advF * .82 - PR + slide, y, baseR, YEL, a * .9, blur=16, add=True)
        blit(f, mF, x0 - PF + slide, y + 4, baseF, (0, 0, 0), a * .45, blur=10, dy=6); blit(f, mR, x0 + advF * .82 - PR + slide, y, baseR, (0, 0, 0), a * .5, blur=10, dy=7)
        blit(f, mF, x0 - PF + slide, y + 4, baseF, YEL, a); blit(f, mR, x0 + advF * .82 - PR + slide, y, baseR, YEL, a)
    for txt, dy in ((white_above, -size * .86), (white_below, size * .42)):
        if txt:
            ss = fit('sans', [txt], 46, 640, 700, -.03); m2, adv2, base2, P2 = tm(txt, 'sans', ss, 700, -.03 * ss)
            blit(f, m2, x - adv2 / 2 - P2, y + dy, base2, (0, 0, 0), a * .55, blur=9, dy=5); blit(f, m2, x - adv2 / 2 - P2, y + dy, base2, WH, a)
def caption_small(f, words, y, hi=(), cx=540, u=1.0, a=1.0, size=40):
    """the inspo caption: SMALL plain white Inter 700, key words acid yellow, dark soft shadow, words rise in one after another"""
    caption(f, words, y, hi=hi, a=a, size=size, cx=cx, u=u)

def frame_shift(fr, shift=200, zoom=1.0):
    """full-width footage pushed DOWN by `shift` px (bottom of the torso is cropped); the new headroom continues the wall tone. No side strips, no scale-down."""
    can = np.zeros((1920, 1080, 3), np.uint8); can[shift:] = fr[:1920 - shift]
    row = cv2.GaussianBlur(fr[4:30].mean(0, keepdims=True), (0, 0), 50); band = np.repeat(row, shift, 0).astype(np.float32)
    g = np.linspace(0, 1, 26, dtype=np.float32)[:, None, None]; can[:shift] = band.astype(np.uint8)
    can[shift - 26:shift] = (band[:26] * (1 - g) + fr[:26].astype(np.float32) * g).astype(np.uint8)                     # feather the seam
    if zoom != 1.0: can = cv2.warpAffine(can, np.float32([[zoom, 0, 540 - zoom * 540], [0, zoom, 1300 - zoom * 1300]]), (1080, 1920), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return can

def grade_cine(raw):
    """her grade, measured (inspo frame Lab: mean L 41.6, p5 0.8, p95 88.6, a +2.6, b +16, wall RGB 188/176/131 cream-olive, rich saturation) applied to the user's room:
    deeper crushed blacks and a darker mid (cinematic), pink/orange pulled toward cream-olive (a -6, b -5.5), filmic S-curve, highlight roll-off, soft bloom, vignette."""
    f = raw.astype(np.float32) / 255
    lab = cv2.cvtColor(f, cv2.COLOR_BGR2LAB); L, A, B = lab[..., 0], lab[..., 1], lab[..., 2]
    x = np.clip((L - 9) / 74, 0, 1.15); x = x ** 1.32                                                    # crush blacks, darker mids
    x = x + (x - .5) * (1 - np.abs(x - .5) * 2).clip(0, 1) * .18                                         # S-curve
    L2 = np.clip(x * 91, 0, 100)
    skin = np.clip((A - 8) / 6, 0, 1) * np.clip((B - 14) / 8, 0, 1)                                      # protect warm skin from the green push
    A2 = A - 6.0 * (1 - .55 * skin); B2 = B - 5.5 * (1 - .45 * skin)
    out = cv2.cvtColor(np.dstack([L2, A2, B2]).astype(np.float32), cv2.COLOR_LAB2BGR)
    out = np.clip(out, 0, 1)
    lum = (out[..., 0] * .114 + out[..., 1] * .587 + out[..., 2] * .299); mx = out.max(2); mn = out.min(2); chroma = (mx - mn)
    wallm = np.clip((lum - .38) / .25, 0, 1) * np.clip(1 - chroma / .22, 0, 1); wallm = cv2.GaussianBlur(wallm, (0, 0), 6)[..., None]                 # pale low-chroma surfaces (the wall) -> her cream-olive
    out = out * (1 - wallm * .85) + out * np.array([.66, .95, 1.0], np.float32) * wallm * .85
    bl = cv2.GaussianBlur(np.clip(out - .62, 0, 1) * 2.6, (0, 0), 22); out = 1 - (1 - out) * (1 - bl * .16)
    H, W = out.shape[:2]; yy, xx = np.mgrid[0:H, 0:W].astype(np.float32); d = ((xx - W / 2) / (W * .75)) ** 2 + ((yy - H * .5) / (H * .7)) ** 2
    out = out * (1 - .2 * np.clip(d, 0, 1))[..., None]
    hsv = cv2.cvtColor((np.clip(out, 0, 1) * 255).astype(np.uint8), cv2.COLOR_BGR2HSV).astype(np.float32); hsv[..., 1] = np.clip(hsv[..., 1] * 1.12, 0, 255)
    return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
